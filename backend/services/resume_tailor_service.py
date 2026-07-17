import json
import re
from typing import Any

from fastapi import UploadFile
from ollama import chat

from backend.repositories.profile_repository import ProfileRepository
from backend.services.resume_service import ResumeService


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
    ):
        self.profile_repository = profile_repository
        self.resume_service = resume_service

    async def tailor_for_user(
        self,
        user_id: int,
        file: UploadFile,
        job_description: str,
    ) -> dict[str, Any]:
        if not job_description.strip():
            raise ValueError(
                "Job description cannot be empty."
            )

        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before tailoring a resume."
            )

        try:
            resume_text = await self.resume_service.extract_text(
                file
            )
        except ValueError:
            raise
        except Exception as error:
            raise ResumeTailorError(
                "The uploaded resume could not be read."
            ) from error

        prompt = self._build_prompt(
            resume_text,
            job_description,
            profile,
        )

        try:
            response = chat(
                model="qwen3:8b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            result = self._parse_response(
                response.message.content
            )
        except ResumeTailorError:
            raise
        except Exception as error:
            raise ResumeTailorError(
                "Resume tailoring is temporarily unavailable."
            ) from error

        return result

    @staticmethod
    def _build_prompt(
        resume_text: str,
        job_description: str,
        profile: Any,
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
- Return only valid JSON using this shape:

{{
    "summary": "",
    "skills": [],
    "experience": []
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
            "summary": str(result.get("summary", "")),
            "skills": list(result.get("skills") or []),
            "experience": list(result.get("experience") or []),
        }
