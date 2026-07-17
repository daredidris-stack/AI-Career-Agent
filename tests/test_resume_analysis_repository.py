import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database.database import Base
from backend.models.resume_analysis import ResumeAnalysis
from backend.models.user import User
from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)


class ResumeAnalysisRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        session = sessionmaker(bind=self.engine)
        self.db = session()
        user = User(email="resume@example.com", password_hash="hash")
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        self.user_id = user.id
        self.repository = ResumeAnalysisRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_creates_and_reads_latest_analysis(self):
        first = self.repository.create(
            self.user_id,
            "first.pdf",
            {
                "resume_score": 70,
                "ats_score": 65,
                "strengths": ["Clear"],
                "improvements": ["Add metrics"],
                "skills": ["AWS", "Linux"],
            },
        )
        second = self.repository.create(
            self.user_id,
            "second.pdf",
            {
                "resume_score": 85,
                "ats_score": 80,
                "strengths": [],
                "improvements": [],
                "skills": ["AWS", "Python"],
            },
        )

        latest = self.repository.get_latest_by_user_id(self.user_id)

        self.assertIsInstance(first, ResumeAnalysis)
        self.assertEqual(latest.id, second.id)
        self.assertEqual(latest.resume_score, 85)
        self.assertEqual(latest.filename, "second.pdf")
        self.assertEqual(
            self.repository.get_latest_skills_by_user_id(self.user_id),
            ["AWS", "Python"],
        )

    def test_returns_none_without_analysis(self):
        self.assertIsNone(
            self.repository.get_latest_by_user_id(self.user_id)
        )


if __name__ == "__main__":
    unittest.main()
