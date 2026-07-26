from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.user import User
from backend.models.profile import Profile
from backend.models.resume_analysis import ResumeAnalysis
from backend.models.career_document import CareerDocument
from backend.models.career_document_revision import CareerDocumentRevision
from backend.models.job_application import JobApplication
from backend.models.ai_usage_event import AIUsageEvent


class UserRepository:

    def __init__(self, db: Session):
        self.db = db


    def get_by_email(self, email: str):

        return (
            self.db.query(User)
            .filter(func.lower(User.email) == email.strip().casefold())
            .first()
        )

    def get_by_google_subject(self, subject: str):
        return (
            self.db.query(User)
            .filter(User.google_subject == subject)
            .first()
        )


    def create_user(
        self,
        email: str,
        password_hash: str,
        terms_accepted_at=None,
        terms_version: str | None = None,
        google_subject: str | None = None,
        is_email_verified: bool = False,
        first_name: str | None = None,
        last_name: str | None = None,
    ):

        user = User(
            email=email.strip().casefold(),
            password_hash=password_hash,
            terms_accepted_at=terms_accepted_at,
            terms_version=terms_version,
            google_subject=google_subject,
            is_email_verified=is_email_verified,
            first_name=first_name,
            last_name=last_name,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user


    def get_by_id(self, user_id: int):

        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_stripe_customer_id(self, customer_id: str):
        return self.db.query(User).filter(
            User.stripe_customer_id == customer_id
        ).first()

    def save(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.db.query(AIUsageEvent).filter(
            AIUsageEvent.user_id == user.id
        ).delete(synchronize_session=False)
        self.db.query(JobApplication).filter(
            JobApplication.user_id == user.id
        ).delete(synchronize_session=False)
        self.db.query(CareerDocumentRevision).filter(
            CareerDocumentRevision.user_id == user.id
        ).delete(synchronize_session=False)
        self.db.query(CareerDocument).filter(
            CareerDocument.user_id == user.id
        ).delete(synchronize_session=False)
        self.db.query(ResumeAnalysis).filter(
            ResumeAnalysis.user_id == user.id
        ).delete(synchronize_session=False)
        self.db.query(Profile).filter(
            Profile.user_id == user.id
        ).delete(synchronize_session=False)
        self.db.delete(user)
        self.db.commit()
