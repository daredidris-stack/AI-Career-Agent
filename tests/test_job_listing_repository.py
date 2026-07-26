import unittest
from datetime import timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.core.time import utc_now
from backend.database.database import Base
from backend.repositories.job_listing_repository import JobListingRepository


class JobListingRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.repository = JobListingRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_upsert_deduplicates_and_preserves_richer_description(self):
        now = utc_now()
        first = {
            "source": "First source",
            "source_job_id": "one",
            "title": "Registered Nurse",
            "company": "Example Health",
            "location": "Austin, Texas",
            "description": "Short description",
            "apply_url": "https://jobs.example.com/one",
            "skills": ["Patient care"],
            "updated": now.isoformat(),
        }
        richer = {
            **first,
            "source": "Employer index",
            "source_job_id": "two",
            "description": "A much longer and complete nursing job description.",
            "apply_url": "https://employer.example/jobs/two",
        }

        created = self.repository.upsert_many([first], seen_at=now)
        updated = self.repository.upsert_many(
            [richer],
            seen_at=now + timedelta(minutes=5),
        )
        jobs = self.repository.search("Registered Nurse", "Worldwide")

        self.assertEqual(created["created"], 1)
        self.assertEqual(updated["updated"], 1)
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["source"], "Employer index")
        self.assertEqual(jobs[0]["description"], richer["description"])
        self.assertEqual(jobs[0]["apply_url"], richer["apply_url"])
        self.assertTrue(jobs[0]["cached"])

    def test_search_filters_terms_and_location(self):
        self.repository.upsert_many([
            {
                "title": "Warehouse Manager",
                "company": "Logistics Co",
                "location": "Toronto, Canada",
                "description": "Lead warehouse operations.",
                "apply_url": "https://example.com/warehouse",
            },
            {
                "title": "Restaurant Manager",
                "company": "Food Co",
                "location": "Madrid, Spain",
                "description": "Lead restaurant operations.",
                "apply_url": "https://example.com/restaurant",
            },
        ])

        jobs = self.repository.search("Warehouse Manager", "Canada")

        self.assertEqual([job["title"] for job in jobs], ["Warehouse Manager"])

    def test_expired_and_stale_jobs_are_deactivated(self):
        now = utc_now()
        self.repository.upsert_many([{
            "title": "Accountant",
            "company": "Example Finance",
            "location": "Remote",
            "apply_url": "https://example.com/accountant",
            "expires_at": (now - timedelta(days=1)).isoformat(),
        }], seen_at=now)

        self.assertEqual(
            self.repository.search("Accountant", now=now),
            [],
        )
        changed = self.repository.deactivate_expired(now=now)

        self.assertEqual(changed, 1)
        self.assertEqual(self.repository.search("Accountant"), [])

    def test_stale_jobs_are_hidden_even_before_maintenance_runs(self):
        now = utc_now()
        self.repository.upsert_many([{
            "title": "Operations Manager",
            "company": "Example Logistics",
            "location": "Remote",
            "apply_url": "https://example.com/operations",
            "expires_at": (now + timedelta(days=30)).isoformat(),
        }], seen_at=now - timedelta(days=46))

        jobs = self.repository.search(
            "Operations Manager",
            now=now,
            stale_days=45,
        )
        changed = self.repository.deactivate_expired(
            now=now,
            stale_days=45,
        )

        self.assertEqual(jobs, [])
        self.assertEqual(changed, 1)

    def test_rejects_unsafe_urls_and_prefers_safe_listing_fallback(self):
        counts = self.repository.upsert_many([
            {
                "title": "Safe Role",
                "company": "Example",
                "location": "Remote",
                "apply_url": "javascript:alert(1)",
                "listing_url": "https://jobs.example.com/safe",
            },
            {
                "title": "Unsafe Role",
                "company": "Example",
                "location": "Remote",
                "url": "https://user@jobs.example.com/private",
            },
        ])

        jobs = self.repository.search("Safe Role")

        self.assertEqual(counts, {
            "created": 1,
            "updated": 0,
            "skipped": 1,
        })
        self.assertEqual(
            jobs[0]["apply_url"],
            "https://jobs.example.com/safe",
        )

    def test_empty_normalized_keyword_does_not_return_entire_catalog(self):
        self.repository.upsert_many([{
            "title": "Platform Engineer",
            "company": "Example",
            "location": "Remote",
            "apply_url": "https://jobs.example.com/platform",
        }])

        self.assertEqual(self.repository.search("!"), [])

    def test_timestamp_offsets_are_normalized_to_naive_utc(self):
        self.repository.upsert_many([{
            "title": "Network Engineer",
            "company": "Example",
            "location": "Remote",
            "apply_url": "https://jobs.example.com/network",
            "updated": "2026-07-20T10:00:00-05:00",
        }])

        jobs = self.repository.search("Network Engineer")

        self.assertEqual(jobs[0]["updated"], "2026-07-20T15:00:00Z")


if __name__ == "__main__":
    unittest.main()
