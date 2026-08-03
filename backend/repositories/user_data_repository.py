from sqlalchemy.orm import Session

from backend.models.ai_usage_event import AIUsageEvent
from backend.models.career_document import CareerDocument
from backend.models.career_document_revision import CareerDocumentRevision
from backend.models.job_application import JobApplication
from backend.models.job_library import (
    JobAlertDelivery,
    SavedJob,
    SavedSearch,
)
from backend.models.profile import Profile
from backend.models.resume_analysis import ResumeAnalysis
from backend.models.support_ticket import SupportTicket
from backend.models.interview_practice import InterviewPracticeAttempt


class UserDataRepository:
    def __init__(self, db: Session):
        self.db = db

    def snapshot(self, user_id: int) -> dict:
        return {
            "profile": self.db.query(Profile).filter(
                Profile.user_id == user_id
            ).first(),
            "resume_analyses": self.db.query(ResumeAnalysis).filter(
                ResumeAnalysis.user_id == user_id
            ).all(),
            "career_documents": self.db.query(CareerDocument).filter(
                CareerDocument.user_id == user_id
            ).all(),
            "document_revisions": self.db.query(CareerDocumentRevision).filter(
                CareerDocumentRevision.user_id == user_id
            ).all(),
            "job_applications": self.db.query(JobApplication).filter(
                JobApplication.user_id == user_id
            ).all(),
            "saved_jobs": self.db.query(SavedJob).filter(
                SavedJob.user_id == user_id
            ).all(),
            "saved_searches": self.db.query(SavedSearch).filter(
                SavedSearch.user_id == user_id
            ).all(),
            "job_alert_deliveries": self.db.query(
                JobAlertDelivery
            ).filter(
                JobAlertDelivery.user_id == user_id
            ).all(),
            "support_tickets": self.db.query(SupportTicket).filter(
                SupportTicket.user_id == user_id
            ).all(),
            "interview_practice_attempts": self.db.query(
                InterviewPracticeAttempt
            ).filter(
                InterviewPracticeAttempt.user_id == user_id
            ).all(),
            "ai_usage_events": self.db.query(AIUsageEvent).filter(
                AIUsageEvent.user_id == user_id
            ).all(),
        }
