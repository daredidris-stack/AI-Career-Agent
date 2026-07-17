from typing import Any

from ollama import chat

from backend.repositories.profile_repository import ProfileRepository
from backend.services.career_document_service import CareerDocumentService


class ProfileRequiredError(Exception):
    pass


class CoverLetterError(Exception):
    pass


def _profile_value(
    profile: Any,
    field_name: str,
    default: Any = "",
) -> Any:
    if isinstance(profile, dict):
        return profile.get(field_name, default) or default

    return getattr(profile, field_name, default) or default


class CoverLetterService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        document_service: CareerDocumentService | None = None,
    ):
        self.profile_repository = profile_repository
        self.document_service = document_service

    def generate_for_user(
        self,
        user_id: int,
        resume: str,
        job_description: str,
    ) -> dict[str, str]:
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
                "Create your profile before generating "
                "a cover letter."
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
            cover_letter = str(
                response.message.content
            ).strip()
        except Exception as error:
            raise CoverLetterError(
                "Cover letter generation is temporarily "
                "unavailable."
            ) from error

        if not cover_letter:
            raise CoverLetterError(
                "The AI returned an empty cover letter."
            )

        result = {
            "cover_letter": cover_letter,
        }
        if self.document_service:
            document = self.document_service.create_for_user(
                user_id,
                "cover_letter",
                "Cover Letter",
                cover_letter,
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
You are an expert technical recruiter and professional cover letter writer.

Candidate profile context:
- Current role: {_profile_value(profile, "current_role", "Not provided")}
- Target role: {_profile_value(profile, "target_role", "Not provided")}
- Years of experience: {_profile_value(profile, "years_experience", 0)}
- Technical skills: {_profile_value(profile, "technical_skills", "Not provided")}
- Professional summary: {_profile_value(profile, "professional_summary", "Not provided")}

Candidate resume:
{resume}

Target job description:
{job_description}

Write a professional cover letter of approximately 300 words.

Rules:
- Only mention facts supported by the supplied resume.
- Never invent employers, experience, projects, skills, certifications, achievements, or metrics.
- Use the profile only to understand career direction; do not treat it as evidence for unsupported resume claims.
- Connect relevant resume evidence to the job requirements.
- Use a confident, professional hiring-manager tone.
- End with a professional closing.
- Return only the cover letter.
""".strip()
