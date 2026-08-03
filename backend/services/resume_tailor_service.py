import asyncio
import json
import re
from typing import Any

from fastapi import UploadFile
from ollama import chat
from services.ollama_service import reliable_chat

from backend.repositories.profile_repository import ProfileRepository
from backend.services.candidate_skills import normalize_explicit_skills
from backend.services.resume_service import ResumeService
from backend.services.malware_scan_service import (
    MalwareScannerUnavailableError,
)
from backend.services.resume_parser_service import (
    ResumeParserUnavailableError,
)
from backend.services.career_document_service import CareerDocumentService
from backend.services.resume_template_service import (
    resolve_resume_template_id,
    template_prompt_options,
    validate_template_request,
)
from resume_text_cleaner import clean_resume_text


class ProfileRequiredError(Exception):
    pass


class ResumeTailorError(Exception):
    pass


def _profile_value(
    profile: Any,
    field_name: str,
    default: Any = "",
) -> Any:
    if isinstance(profile, dict):
        return profile.get(field_name, default) or default

    return getattr(profile, field_name, default) or default


class ResumeTailorService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        resume_service: ResumeService,
        document_service: CareerDocumentService | None = None,
    ):
        self.profile_repository = profile_repository
        self.resume_service = resume_service
        self.document_service = document_service

    async def tailor_for_user(
        self,
        user_id: int,
        file: UploadFile | None,
        job_description: str,
        template_id: str = "auto",
    ) -> dict[str, Any]:
        if not job_description.strip():
            raise ValueError(
                "Job description cannot be empty."
            )
        requested_template_id = validate_template_request(template_id)

        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before tailoring a resume."
            )

        if file:
            source_filename = getattr(file, "filename", None) or "resume"
            try:
                resume_text = await self.resume_service.extract_text(file)
            except ValueError:
                raise
            except MalwareScannerUnavailableError:
                raise
            except ResumeParserUnavailableError:
                raise
            except Exception as error:
                raise ResumeTailorError(
                    "The uploaded resume could not be read."
                ) from error
        else:
            resume_text, source_filename = self._latest_resume_for_user(user_id)

        prompt = self._build_prompt(
            resume_text,
            job_description,
            profile,
            requested_template_id,
        )

        try:
            response = await asyncio.to_thread(
                reliable_chat,
                prompt,
                chat_callable=chat,
                response_format="json",
            )
            result = self._parse_response(
                response.message.content
            )
            result["template_id"] = resolve_resume_template_id(
                requested_template_id,
                result.pop("template_id", None),
            )
        except ResumeTailorError:
            raise
        except Exception as error:
            raise ResumeTailorError(
                "Resume tailoring is temporarily unavailable."
            ) from error

        if self.document_service:
            document = self.document_service.create_for_user(
                user_id,
                "tailored_resume",
                f"Tailored {source_filename}",
                json.dumps(result, indent=2),
                source_filename=source_filename,
                job_description=job_description.strip(),
            )
            result["document_id"] = document.id

        return result

    def _latest_resume_for_user(self, user_id: int) -> tuple[str, str]:
        if self.document_service:
            resumes = self.document_service.list_for_user(user_id, "resume")
            if resumes:
                resume = resumes[0]
                return str(resume.content).strip(), (
                    resume.source_filename or resume.title or "resume"
                )
        raise ValueError(
            "Analyze or create a resume before tailoring it."
        )

    @staticmethod
    def _build_prompt(
        resume_text: str,
        job_description: str,
        profile: Any,
        requested_template_id: str = "auto",
    ) -> str:
        return f"""
You are a professional ATS resume writer.

Rewrite wording from the supplied resume to better align with the job description.

Candidate profile context:
- Current role: {_profile_value(profile, "current_role", "Not provided")}
- Target role: {_profile_value(profile, "target_role", "Not provided")}
- Years of experience: {_profile_value(profile, "years_experience", 0)}
- Technical skills: {_profile_value(profile, "technical_skills", "Not provided")}
- Professional summary: {_profile_value(profile, "professional_summary", "Not provided")}

Resume:
{resume_text}

Job description:
{job_description}

Rules:
- Never invent experience, skills, employers, dates, certifications, or projects.
- Only improve and reorganize facts present in the resume.
- Keep all output truthful.
- Do not copy literal Markdown, template instructions, example.com addresses,
  North American 555 phone numbers, or generator commentary.
- Use concise, ATS-friendly language and preserve the candidate's real role,
  employer, dates, education, and contact details when present.
- The requested template is: {requested_template_id}.
- When the requested template is auto, select the best template_id from:
{template_prompt_options()}
- Return only valid JSON using this shape:

{{
    "template_id": "ats-professional",
    "full_name": "",
    "contact_line": "",
    "target_role": "",
    "summary": "",
    "skills": [],
    "experience": [
        {{
            "role": "",
            "company": "",
            "dates": "",
            "bullets": []
        }}
    ],
    "education": [],
    "certifications": [],
    "projects": []
}}
""".strip()

    @staticmethod
    def _parse_response(content: str) -> dict[str, Any]:
        match = re.search(
            r"\{.*\}",
            content,
            re.DOTALL,
        )

        if not match:
            raise ResumeTailorError(
                "The AI response was not valid JSON."
            )

        try:
            result = json.loads(match.group())
        except (TypeError, ValueError) as error:
            raise ResumeTailorError(
                "The AI response was not valid JSON."
            ) from error

        return {
            "template_id": _clean_value(result.get("template_id")),
            "full_name": _clean_value(result.get("full_name")),
            "contact_line": _clean_contact(result.get("contact_line")),
            "target_role": _clean_value(result.get("target_role")),
            "summary": _clean_value(result.get("summary")),
            "skills": normalize_explicit_skills(result.get("skills")),
            "experience": _normalize_experience(result.get("experience")),
            "education": _normalize_string_list(result.get("education")),
            "certifications": _normalize_string_list(
                result.get("certifications")
            ),
            "projects": _normalize_string_list(result.get("projects")),
        }


def _clean_value(value: Any) -> str:
    return clean_resume_text(str(value or "")).strip()


def _clean_contact(value: Any) -> str:
    contact = _clean_value(value)
    folded = contact.casefold()
    if "example.com" in folded:
        return ""
    digits = re.sub(r"\D", "", contact)
    if (
        (len(digits) == 10 and digits.startswith("555"))
        or (len(digits) == 11 and digits.startswith("1555"))
    ):
        return ""
    return contact


def _normalize_string_list(value: Any) -> list[str]:
    if isinstance(value, str):
        values = [value]
    elif isinstance(value, list):
        values = value
    else:
        return []

    normalized = []
    seen = set()
    for item in values:
        text = _clean_value(item)
        key = text.casefold()
        if text and key not in seen:
            normalized.append(text)
            seen.add(key)
    return normalized


def _normalize_experience(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []

    experience = []
    for item in value:
        if isinstance(item, dict):
            entry = {
                "role": _clean_value(item.get("role")),
                "company": _clean_value(item.get("company")),
                "dates": _clean_value(item.get("dates")),
                "bullets": _normalize_string_list(item.get("bullets")),
            }
        else:
            entry = {
                "role": "",
                "company": "",
                "dates": "",
                "bullets": _normalize_string_list([item]),
            }
        if any(entry.values()):
            experience.append(entry)
    return experience
