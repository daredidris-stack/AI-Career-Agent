import unittest
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.core.time import utc_now
from backend.models.user import User
from backend.repositories.job_library_repository import JobLibraryRepository


class JobLibraryRepositoryTests(unittest.TestCase):
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
        self.repository = JobLibraryRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_saved_jobs_are_scoped_to_owner(self):
        self.repository.create_saved_job(
            user_id=self.first_id,
            job_key="a" * 64,
            title="First role",
            company="First company",
            job_data_json="{}",
        )
        self.repository.create_saved_job(
            user_id=self.second_id,
            job_key="b" * 64,
            title="Private role",
            company="Private company",
            job_data_json="{}",
        )

        jobs = self.repository.list_saved_jobs(self.first_id)

        self.assertEqual([job.title for job in jobs], ["First role"])
        self.assertIsNone(
            self.repository.get_saved_job(jobs[0].id, self.second_id)
        )

    def test_saved_searches_are_scoped_to_owner(self):
        first = self.repository.create_search(
            user_id=self.first_id,
            name="Remote SRE",
            filters_json='{"keyword": "SRE"}',
        )
        self.repository.create_search(
            user_id=self.second_id,
            name="Private search",
            filters_json='{"keyword": "Private"}',
        )

        searches = self.repository.list_searches(self.first_id)

        self.assertEqual([search.name for search in searches], ["Remote SRE"])
        self.assertIsNone(
            self.repository.get_search(first.id, self.second_id)
        )

    def test_due_searches_require_opt_in_verified_user_and_due_time(self):
        now = utc_now()
        verified = self.db.get(User, self.first_id)
        verified.is_email_verified = True
        self.db.add_all([
            verified,
            User(
                email="unverified@example.com",
                password_hash="hash",
                is_email_verified=False,
            ),
        ])
        self.db.commit()
        unverified = self.db.query(User).filter_by(
            email="unverified@example.com"
        ).one()
        self.db.add_all([
            self.repository.create_search(
                user_id=self.first_id,
                name="Due",
                filters_json='{"keyword": "SRE"}',
            ),
            self.repository.create_search(
                user_id=self.first_id,
                name="Future",
                filters_json='{"keyword": "SRE"}',
            ),
            self.repository.create_search(
                user_id=self.first_id,
                name="Off",
                filters_json='{"keyword": "SRE"}',
            ),
            self.repository.create_search(
                user_id=unverified.id,
                name="Unverified",
                filters_json='{"keyword": "SRE"}',
            ),
        ])
        searches = {
            item.name: item
            for item in self.repository.list_searches(self.first_id)
        }
        searches["Due"].email_alerts_enabled = True
        searches["Due"].next_alert_at = now - timedelta(minutes=1)
        searches["Future"].email_alerts_enabled = True
        searches["Future"].next_alert_at = now + timedelta(minutes=1)
        unverified_search = self.db.query(
            type(searches["Due"])
        ).filter_by(name="Unverified").one()
        unverified_search.email_alerts_enabled = True
        unverified_search.next_alert_at = now - timedelta(minutes=1)
        self.db.commit()

        result = self.repository.list_due_searches(now, 10)

        self.assertEqual([search.name for search, _ in result], ["Due"])


if __name__ == "__main__":
    unittest.main()
