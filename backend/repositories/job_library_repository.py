from sqlalchemy.orm import Session

from backend.models.job_library import (
    JobAlertDelivery,
    SavedJob,
    SavedSearch,
)
from backend.models.user import User


class JobLibraryRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_saved_jobs(self, user_id: int):
        return (
            self.db.query(SavedJob)
            .filter(SavedJob.user_id == user_id)
            .order_by(SavedJob.updated_at.desc())
            .all()
        )

    def get_saved_job(self, saved_job_id: int, user_id: int):
        return (
            self.db.query(SavedJob)
            .filter(
                SavedJob.id == saved_job_id,
                SavedJob.user_id == user_id,
            )
            .first()
        )

    def get_saved_job_by_key(self, user_id: int, job_key: str):
        return (
            self.db.query(SavedJob)
            .filter(
                SavedJob.user_id == user_id,
                SavedJob.job_key == job_key,
            )
            .first()
        )

    def create_saved_job(self, **values):
        saved_job = SavedJob(**values)
        self.db.add(saved_job)
        self.db.commit()
        self.db.refresh(saved_job)
        return saved_job

    def save_saved_job(self, saved_job):
        self.db.add(saved_job)
        self.db.commit()
        self.db.refresh(saved_job)
        return saved_job

    def delete_saved_job(self, saved_job) -> None:
        self.db.delete(saved_job)
        self.db.commit()

    def list_searches(self, user_id: int):
        return (
            self.db.query(SavedSearch)
            .filter(SavedSearch.user_id == user_id)
            .order_by(SavedSearch.updated_at.desc())
            .all()
        )

    def get_search(self, saved_search_id: int, user_id: int):
        return (
            self.db.query(SavedSearch)
            .filter(
                SavedSearch.id == saved_search_id,
                SavedSearch.user_id == user_id,
            )
            .first()
        )

    def create_search(self, **values):
        saved_search = SavedSearch(**values)
        self.db.add(saved_search)
        self.db.commit()
        self.db.refresh(saved_search)
        return saved_search

    def save_search(self, saved_search):
        self.db.add(saved_search)
        self.db.commit()
        self.db.refresh(saved_search)
        return saved_search

    def delete_search(self, saved_search) -> None:
        self.db.delete(saved_search)
        self.db.commit()

    def list_due_searches(self, due_at, limit: int):
        return (
            self.db.query(SavedSearch, User)
            .join(User, User.id == SavedSearch.user_id)
            .filter(
                SavedSearch.email_alerts_enabled.is_(True),
                SavedSearch.next_alert_at.is_not(None),
                SavedSearch.next_alert_at <= due_at,
                User.is_email_verified.is_(True),
            )
            .order_by(SavedSearch.next_alert_at.asc())
            .limit(limit)
            .all()
        )

    def get_delivery_by_batch(
        self,
        saved_search_id: int,
        batch_key: str,
    ):
        return (
            self.db.query(JobAlertDelivery)
            .filter(
                JobAlertDelivery.saved_search_id == saved_search_id,
                JobAlertDelivery.batch_key == batch_key,
            )
            .first()
        )

    def create_delivery(self, **values):
        delivery = JobAlertDelivery(**values)
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def save_delivery(self, delivery):
        self.db.add(delivery)
        self.db.commit()
        self.db.refresh(delivery)
        return delivery

    def list_deliveries_for_user(
        self,
        user_id: int,
        limit: int = 20,
    ):
        return (
            self.db.query(JobAlertDelivery)
            .filter(JobAlertDelivery.user_id == user_id)
            .order_by(JobAlertDelivery.created_at.desc())
            .limit(limit)
            .all()
        )
