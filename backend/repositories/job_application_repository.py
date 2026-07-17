from sqlalchemy.orm import Session

from backend.models.job_application import JobApplication


class JobApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_user(self, user_id: int, status: str | None = None):
        query = self.db.query(JobApplication).filter(
            JobApplication.user_id == user_id
        )
        if status:
            query = query.filter(JobApplication.status == status)
        return query.order_by(JobApplication.updated_at.desc()).all()

    def get_for_user(self, application_id: int, user_id: int):
        return self.db.query(JobApplication).filter(
            JobApplication.id == application_id,
            JobApplication.user_id == user_id,
        ).first()

    def create(self, **values):
        application = JobApplication(**values)
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def save(self, application):
        self.db.add(application)
        self.db.commit()
        self.db.refresh(application)
        return application

    def delete(self, application) -> None:
        self.db.delete(application)
        self.db.commit()

    def counts_by_status(self, user_id: int) -> dict[str, int]:
        applications = self.list_for_user(user_id)
        counts: dict[str, int] = {}
        for application in applications:
            counts[application.status] = counts.get(application.status, 0) + 1
        return counts
