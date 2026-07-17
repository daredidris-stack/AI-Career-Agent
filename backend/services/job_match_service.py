import json
import re
from typing import Any

from ollama import chat

from backend.repositories.profile_repository import ProfileRepository
from backend.services.career_document_service import CareerDocumentService


class ProfileRequiredError(Exception):
    pass


class JobMatchError(Exception):
    pass


def _profile_value(
    profile: Any,
    field_name: str,
    default: Any = "",
) -> Any:
    if isinstance(profile, dict):
        return profile.get(field_name, default) or default

    return getattr(profile, field_name, default) or default


class JobMatchService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        document_service: CareerDocumentService | None = None,
    ):
        self.profile_repository = profile_repository
        self.document_service = document_service

    def match_for_user(
        self,
        user_id: int,
        resume: str,
        job_description: str,
    ) -> dict[str, Any]:
        resume = resume.strip()
        job_description = job_description.strip()

        if not resume:
            raise ValueError("Resume cannot be empty.")

        if not job_description:
            raise ValueError(
                "Job description cannot be empty."
            )

        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before matching a job."
            )

        prompt = self._build_prompt(
            profile,
            resume,
            job_description,
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
        except JobMatchError:
            raise
        except Exception as error:
            raise JobMatchError(
                "Job matching is temporarily unavailable."
            ) from error

        if self.document_service:
            document = self.document_service.create_for_user(
                user_id,
                "job_match",
                "Job Match Report",
                json.dumps(result, indent=2),
                job_description=job_description,
            )
            result["document_id"] = document.id
        return result

    @staticmethod
    def _build_prompt(
        profile: Any,
        resume: str,
        job_description: str,
    ) -> str:
        return f"""
You are an expert technical recruiter.

Candidate profile context:
- Current role: {_profile_value(profile, "current_role", "Not provided")}
- Target role: {_profile_value(profile, "target_role", "Not provided")}
- Years of experience: {_profile_value(profile, "years_experience", 0)}
- Technical skills: {_profile_value(profile, "technical_skills", "Not provided")}
- Professional summary: {_profile_value(profile, "professional_summary", "Not provided")}

Resume:
{resume}

Job description:
{job_description}

Evaluate direct experience, transferable experience, technical skills, career progression, and missing requirements.

Rules:
- Base all evidence on the supplied resume.
- Use the profile only for career context, not as proof of unsupported resume claims.
- Never invent candidate experience or skills.
- Use a realistic match score from 0 to 100.
- Return only valid JSON using this shape:

{{
    "match_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "recommendation": ""
}}
""".strip()

    @staticmethod
    def _parse_response(content: str) -> dict[str, Any]:
        match = re.search(
            r"\{.*\}",
            str(content),
            re.DOTALL,
        )

        if not match:
            raise JobMatchError(
                "The AI response was not valid JSON."
            )

        try:
            result = json.loads(match.group())
            match_score = int(result.get("match_score", 0))
        except (TypeError, ValueError) as error:
            raise JobMatchError(
                "The AI response was not valid JSON."
            ) from error

        matching_skills = result.get("matching_skills")
        missing_skills = result.get("missing_skills")

        if not isinstance(matching_skills, list):
            raise JobMatchError(
                "The AI response contained invalid matching skills."
            )

        if not isinstance(missing_skills, list):
            raise JobMatchError(
                "The AI response contained invalid missing skills."
            )

        return {
            "match_score": max(0, min(100, match_score)),
            "matching_skills": [
                str(skill)
                for skill in matching_skills
            ],
            "missing_skills": [
                str(skill)
                for skill in missing_skills
            ],
            "recommendation": str(
                result.get("recommendation", "")
            ),
        }
