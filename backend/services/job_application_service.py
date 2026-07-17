from typing import Any

from backend.core.time import utc_now
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
    def __init__(self, repository: JobApplicationRepository):
        self.repository = repository

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
        if cleaned.get("status") == "applied" and not cleaned.get("applied_at"):
            cleaned["applied_at"] = utc_now()
        return self.repository.create(user_id=user_id, **cleaned)

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

    @staticmethod
    def _clean(values: dict[str, Any]) -> dict[str, Any]:
        return {
            key: value.strip() if isinstance(value, str) else value
            for key, value in values.items()
        }
