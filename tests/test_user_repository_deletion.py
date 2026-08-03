import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
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
from backend.models.user import User
from backend.models.support_ticket import SupportTicket
from backend.models.interview_practice import InterviewPracticeAttempt
from backend.repositories.user_repository import UserRepository


class UserRepositoryDeletionTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_account_deletion_removes_all_owned_records(self):
        user = User(email="delete@example.com", password_hash="hash")
        self.db.add(user)
        self.db.commit()
        document = CareerDocument(
            user_id=user.id,
            kind="resume",
            title="Resume",
            content="Content",
        )
        saved_search = SavedSearch(
            user_id=user.id,
            name="Saved search",
            filters_json='{"keyword": "Engineer"}',
        )
        self.db.add_all([
            Profile(user_id=user.id),
            ResumeAnalysis(
                user_id=user.id,
                filename="resume.pdf",
                resume_score=80,
                ats_score=75,
                strengths="[]",
                improvements="[]",
                extracted_skills="[]",
            ),
            document,
            JobApplication(
                user_id=user.id,
                company="Example",
                role="Engineer",
            ),
            SavedJob(
                user_id=user.id,
                job_key="a" * 64,
                title="Saved role",
                company="Example",
                job_data_json="{}",
            ),
            saved_search,
            SupportTicket(
                user_id=user.id,
                category="feedback",
                subject="Delete this request",
                message="This should be deleted with the account.",
            ),
            InterviewPracticeAttempt(
                user_id=user.id,
                role="Engineer",
                interview_type="General interview",
                question="Tell me about yourself.",
                answer="This is a sufficiently detailed practice answer.",
                score=50,
                rubric_json="{}",
            ),
            AIUsageEvent(user_id=user.id, feature="job_match"),
        ])
        self.db.flush()
        self.db.add_all([
            CareerDocumentRevision(
                document_id=document.id,
                user_id=user.id,
                title="Old resume",
                content="Old content",
            ),
            JobAlertDelivery(
                user_id=user.id,
                saved_search_id=saved_search.id,
                batch_key="b" * 64,
                status="sent",
                match_count=1,
            ),
        ])
        self.db.commit()

        UserRepository(self.db).delete_user(user)

        for model in (
            User,
            Profile,
            ResumeAnalysis,
            CareerDocument,
            CareerDocumentRevision,
            JobApplication,
            SavedJob,
            SavedSearch,
            JobAlertDelivery,
            SupportTicket,
            InterviewPracticeAttempt,
            AIUsageEvent,
        ):
            self.assertEqual(self.db.query(model).count(), 0)


if __name__ == "__main__":
    unittest.main()
