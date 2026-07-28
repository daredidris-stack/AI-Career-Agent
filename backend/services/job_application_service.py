from typing import Any
from urllib.parse import urlparse

from backend.core.time import utc_now
from backend.repositories.career_document_repository import (
    CareerDocumentRepository,
)
from backend.repositories.job_application_repository import (
    JobApplicationRepository,
)


APPLICATION_STATUSES = {
    "saved",
    "preparing",
    "applied",
    "interview",
    "offer",
    "rejected",
    "archived",
}


class ApplicationNotFoundError(Exception):
    pass


class JobApplicationService:
    def __init__(
        self,
        repository: JobApplicationRepository,
        document_repository: CareerDocumentRepository,
    ):
        self.repository = repository
        self.document_repository = document_repository

    def list_for_user(self, user_id: int, status: str | None = None):
        self._validate_status(status)
        return self.repository.list_for_user(user_id, status)

    def get_for_user(self, user_id: int, application_id: int):
        application = self.repository.get_for_user(application_id, user_id)
        if not application:
            raise ApplicationNotFoundError()
        return application

    def create_for_user(self, user_id: int, values: dict[str, Any]):
        self._validate_status(values.get("status"))
        cleaned = self._clean(values)
        if not cleaned.get("company") or not cleaned.get("role"):
            raise ValueError("Company and role are required.")
        self._validate_documents(user_id, cleaned)
        if cleaned.get("status") == "applied" and not cleaned.get("applied_at"):
            cleaned["applied_at"] = utc_now()
        return self.repository.create(user_id=user_id, **cleaned)

    def prepare_for_user(self, user_id: int, values: dict[str, Any]):
        cleaned = self._clean(values)
        if not cleaned.pop("review_confirmed", False):
            raise ValueError("Review the application package before continuing.")
        if not cleaned.pop("manual_submission_confirmed", False):
            raise ValueError(
                "Confirm that you will review and submit the employer form."
            )
        if not cleaned.get("company") or not cleaned.get("role"):
            raise ValueError("Company and role are required.")

        job_url = self._safe_application_url(cleaned.get("job_url"))
        cleaned["job_url"] = job_url
        self._validate_documents(
            user_id,
            cleaned,
            require_resume=True,
        )
        cleaned["package_reviewed_at"] = utc_now()

        existing = self.repository.get_by_job_url(user_id, job_url)
        if existing:
            preserved_status = existing.status
            for field, value in cleaned.items():
                setattr(existing, field, value)
            if preserved_status in {
                "applied",
                "interview",
                "offer",
                "rejected",
                "archived",
            }:
                existing.status = preserved_status
            else:
                existing.status = "preparing"
            return self.repository.save(existing)

        return self.repository.create(
            user_id=user_id,
            status="preparing",
            **cleaned,
        )

    def update_for_user(
        self,
        user_id: int,
        application_id: int,
        values: dict[str, Any],
    ):
        application = self.get_for_user(user_id, application_id)
        self._validate_status(values.get("status"))
        cleaned = self._clean(values)
        if not cleaned.get("company") or not cleaned.get("role"):
            raise ValueError("Company and role are required.")
        self._validate_documents(user_id, cleaned)
        if cleaned.get("status") == "applied" and not application.applied_at:
            cleaned["applied_at"] = cleaned.get("applied_at") or utc_now()
        for field, value in cleaned.items():
            setattr(application, field, value)
        return self.repository.save(application)

    def delete_for_user(self, user_id: int, application_id: int) -> None:
        self.repository.delete(self.get_for_user(user_id, application_id))

    @staticmethod
    def _validate_status(status: str | None) -> None:
        if status and status not in APPLICATION_STATUSES:
            raise ValueError("Unsupported application status.")

    def _validate_documents(
        self,
        user_id: int,
        values: dict[str, Any],
        require_resume: bool = False,
    ) -> None:
        resume_id = values.get("resume_document_id")
        if require_resume and not resume_id:
            raise ValueError("Select a resume before continuing.")
        if resume_id:
            resume = self.document_repository.get_for_user(
                resume_id,
                user_id,
            )
            if not resume or resume.kind not in {"resume", "tailored_resume"}:
                raise ValueError("The selected resume is not available.")

        cover_letter_id = values.get("cover_letter_document_id")
        if cover_letter_id:
            cover_letter = self.document_repository.get_for_user(
                cover_letter_id,
                user_id,
            )
            if not cover_letter or cover_letter.kind != "cover_letter":
                raise ValueError(
                    "The selected cover letter is not available."
                )

    @staticmethod
    def _safe_application_url(value: Any) -> str:
        candidate = str(value or "").strip()
        parsed = urlparse(candidate)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise ValueError(
                "A secure official application URL is required."
            )
        return candidate

    @staticmethod
    def _clean(values: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value.strip() if isinstance(value, str) else value
            for key, value in values.items()
        }
