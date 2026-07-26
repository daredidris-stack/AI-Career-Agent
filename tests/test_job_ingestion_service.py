import unittest
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.core.time import utc_now
from backend.services.job_ingestion_service import JobIngestionService


class JobIngestionServiceTests(unittest.TestCase):
    def setUp(self):
        self.listing_repository = Mock()
        self.listing_repository.get_sync_state.return_value = None
        self.listing_repository.upsert_many.return_value = {
            "created": 1,
            "updated": 0,
            "skipped": 0,
        }
        self.listing_repository.deactivate_expired.return_value = 0
        self.profile_repository = Mock()
        self.profile_repository.list_job_search_targets.return_value = [
            ("Registered Nurse", "Worldwide")
        ]
        self.provider = Mock(return_value=[{
            "title": "Registered Nurse",
            "company": "Example Health",
            "location": "San Diego, California",
            "apply_url": "https://example.com/nurse",
        }])
        self.service = JobIngestionService(
            self.listing_repository,
            self.profile_repository,
            self.provider,
        )

    def test_initial_sync_backfills_and_records_success(self):
        now = utc_now()

        report = self.service.run_once(now=now)

        self.provider.assert_called_once()
        self.assertEqual(
            self.provider.call_args.kwargs["time_frame"],
            "6m",
        )
        stored_jobs = self.listing_repository.upsert_many.call_args.args[0]
        self.assertEqual(stored_jobs[0]["source"], "Employer index")
        self.assertEqual(report["created"], 1)
        success = self.listing_repository.record_sync_success.call_args.kwargs
        self.assertEqual(success["keyword"], "Registered Nurse")
        self.assertGreater(success["next_sync_at"], now)

    def test_recurring_sync_uses_twenty_four_hour_window(self):
        now = utc_now()
        self.listing_repository.get_sync_state.return_value = SimpleNamespace(
            last_success_at=now - timedelta(days=1),
            next_sync_at=now - timedelta(minutes=1),
        )

        self.service.run_once(now=now)

        self.assertEqual(
            self.provider.call_args.kwargs["time_frame"],
            "24h",
        )

    def test_not_yet_due_target_is_skipped(self):
        now = utc_now()
        self.listing_repository.get_sync_state.return_value = SimpleNamespace(
            last_success_at=now,
            next_sync_at=now + timedelta(hours=1),
        )

        report = self.service.run_once(now=now)

        self.provider.assert_not_called()
        self.assertEqual(report["skipped"], 1)

    @patch(
        "backend.services.job_ingestion_service."
        "JOB_INGESTION_RETRY_SECONDS",
        300,
    )
    def test_failure_is_sanitized_and_schedules_retry(self):
        now = utc_now()
        self.provider.side_effect = RuntimeError(
            "request contained sensitive-provider-token"
        )

        report = self.service.run_once(now=now)

        failure = self.listing_repository.record_sync_failure.call_args.kwargs
        self.assertEqual(report["failed"], 1)
        self.assertEqual(failure["error_message"], "Job ingestion failed.")
        self.assertNotIn("sensitive", failure["error_message"])
        self.assertEqual(
            failure["next_sync_at"],
            now + timedelta(seconds=300),
        )
        self.listing_repository.rollback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
