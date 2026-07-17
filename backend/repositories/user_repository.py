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
            .filter(User.email == email)
            .first()
        )


    def create_user(
        self,
        email: str,
        password_hash: str,
        terms_accepted_at=None,
        terms_version: str | None = None,
    ):

        user = User(
            email=email,
            password_hash=password_hash,
            terms_accepted_at=terms_accepted_at,
            terms_version=terms_version,
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
