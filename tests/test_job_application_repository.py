import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.models.user import User
from backend.repositories.job_application_repository import (
    JobApplicationRepository,
)


class JobApplicationRepositoryTests(unittest.TestCase):
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
        self.repository = JobApplicationRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_application_lookup_is_scoped_to_owner(self):
        application = self.repository.create(
            user_id=self.first_id,
            company="Example",
            role="Engineer",
            status="saved",
        )

        self.assertIsNone(
            self.repository.get_for_user(application.id, self.second_id)
        )
        self.assertEqual(
            self.repository.get_for_user(application.id, self.first_id).role,
            "Engineer",
        )

    def test_list_filters_status_without_leaking_other_users(self):
        self.repository.create(
            user_id=self.first_id,
            company="One",
            role="Engineer",
            status="applied",
        )
        self.repository.create(
            user_id=self.first_id,
            company="Two",
            role="Engineer",
            status="saved",
        )
        self.repository.create(
            user_id=self.second_id,
            company="Private",
            role="Engineer",
            status="applied",
        )

        applications = self.repository.list_for_user(
            self.first_id, "applied"
        )

        self.assertEqual(len(applications), 1)
        self.assertEqual(applications[0].company, "One")


if __name__ == "__main__":
    unittest.main()
