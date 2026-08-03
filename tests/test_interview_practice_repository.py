import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.models.user import User
from backend.repositories.interview_practice_repository import (
    InterviewPracticeRepository,
)


class InterviewPracticeRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        self.db = sessionmaker(bind=self.engine)()
        Base.metadata.create_all(self.engine)
        first = User(email="first@example.com", password_hash="hash")
        second = User(email="second@example.com", password_hash="hash")
        self.db.add_all([first, second])
        self.db.commit()
        self.first_id = first.id
        self.second_id = second.id
        self.repository = InterviewPracticeRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_attempt_history_is_owner_scoped(self):
        common = {
            "role": "Engineer",
            "interview_type": "Behavioral interview",
            "answer": "A detailed practice answer that is long enough.",
            "score": 70,
            "rubric_json": "{}",
        }
        self.repository.create(
            user_id=self.first_id,
            question="First question",
            **common,
        )
        self.repository.create(
            user_id=self.second_id,
            question="Private question",
            **common,
        )

        result = self.repository.list_for_user(self.first_id)

        self.assertEqual(
            [attempt.question for attempt in result],
            ["First question"],
        )


if __name__ == "__main__":
    unittest.main()
