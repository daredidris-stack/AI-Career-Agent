import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.models.career_document import CareerDocument
from backend.models.career_document_revision import CareerDocumentRevision
from backend.models.ai_usage_event import AIUsageEvent
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
from backend.repositories.user_data_repository import UserDataRepository


class UserDataRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        first = User(email="first@example.com", password_hash="hash")
        second = User(email="second@example.com", password_hash="hash")
        self.db.add_all([first, second])
        self.db.commit()
        self.first_id = first.id
        self.second_id = second.id

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_export_snapshot_is_scoped_to_authenticated_owner(self):
        first_document = CareerDocument(
            user_id=self.first_id,
            kind="resume",
            title="First resume",
            content="First content",
        )
        second_document = CareerDocument(
            user_id=self.second_id,
            kind="resume",
            title="Private resume",
            content="Private content",
        )
        self.db.add_all([
            Profile(user_id=self.first_id, city="First city"),
            Profile(user_id=self.second_id, city="Private city"),
            first_document,
            second_document,
        ])
        self.db.flush()
        for user_id, document, marker in (
            (self.first_id, first_document, "First"),
            (self.second_id, second_document, "Private"),
        ):
            saved_search = SavedSearch(
                user_id=user_id,
                name=f"{marker} search",
                filters_json='{"keyword": "Engineer"}',
            )
            self.db.add_all([
                CareerDocumentRevision(
                    document_id=document.id,
                    user_id=user_id,
                    title=f"{marker} revision",
                    content=f"{marker} revision content",
                ),
                ResumeAnalysis(
                    user_id=user_id,
                    filename=f"{marker.lower()}.pdf",
                    resume_score=80,
                    ats_score=75,
                ),
                JobApplication(
                    user_id=user_id,
                    company=f"{marker} company",
                    role="Engineer",
                    status="saved",
                ),
                SavedJob(
                    user_id=user_id,
                    job_key=(marker.lower()[0] * 64),
                    title=f"{marker} saved role",
                    company=f"{marker} saved company",
                    job_data_json="{}",
                ),
                saved_search,
                SupportTicket(
                    user_id=user_id,
                    category="feedback",
                    subject=f"{marker} request",
                    message=f"{marker} support message",
                ),
                InterviewPracticeAttempt(
                    user_id=user_id,
                    role="Engineer",
                    interview_type="Behavioral interview",
                    question=f"{marker} question",
                    answer=f"{marker} answer with enough detail to store.",
                    score=75,
                    rubric_json="{}",
                ),
                AIUsageEvent(user_id=user_id, feature=f"{marker} feature"),
            ])
            self.db.flush()
            self.db.add(JobAlertDelivery(
                user_id=user_id,
                saved_search_id=saved_search.id,
                batch_key=marker.lower()[0] * 64,
                status="sent",
                match_count=1,
            ))
        self.db.commit()

        result = UserDataRepository(self.db).snapshot(self.first_id)

        self.assertEqual(result["profile"].city, "First city")
        self.assertEqual(
            [document.title for document in result["career_documents"]],
            ["First resume"],
        )
        self.assertEqual(
            [item.title for item in result["document_revisions"]],
            ["First revision"],
        )
        self.assertEqual(
            [item.filename for item in result["resume_analyses"]],
            ["first.pdf"],
        )
        self.assertEqual(
            [item.company for item in result["job_applications"]],
            ["First company"],
        )
        self.assertEqual(
            [item.title for item in result["saved_jobs"]],
            ["First saved role"],
        )
        self.assertEqual(
            [item.name for item in result["saved_searches"]],
            ["First search"],
        )
        self.assertEqual(
            [item.status for item in result["job_alert_deliveries"]],
            ["sent"],
        )
        self.assertEqual(
            [item.subject for item in result["support_tickets"]],
            ["First request"],
        )
        self.assertEqual(
            [
                item.question
                for item in result["interview_practice_attempts"]
            ],
            ["First question"],
        )
        self.assertEqual(
            [item.feature for item in result["ai_usage_events"]],
            ["First feature"],
        )


if __name__ == "__main__":
    unittest.main()
