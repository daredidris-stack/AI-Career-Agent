import sys
import unittest
from unittest.mock import Mock, patch

from backend.jobs import sync_job_catalog


class SyncJobCatalogTests(unittest.TestCase):
    @patch.object(sync_job_catalog, "FANTASTIC_JOBS_API_KEY", "")
    @patch.object(sync_job_catalog, "SessionLocal")
    def test_run_once_requires_provider_key_before_opening_database(
        self,
        session_local,
    ):
        with self.assertRaisesRegex(
            RuntimeError,
            "FANTASTIC_JOBS_API_KEY is required",
        ):
            sync_job_catalog.run_once()

        session_local.assert_not_called()

    @patch.object(sync_job_catalog, "FANTASTIC_JOBS_API_KEY", "test-key")
    @patch.object(sync_job_catalog, "JobIngestionService")
    @patch.object(sync_job_catalog, "SessionLocal")
    def test_run_once_closes_database_session(
        self,
        session_local,
        service_class,
    ):
        db = Mock()
        session_local.return_value = db
        service_class.return_value.run_once.return_value = {"targets": 0}

        report = sync_job_catalog.run_once(force=True)

        self.assertEqual(report, {"targets": 0})
        service_class.return_value.run_once.assert_called_once_with(force=True)
        db.close.assert_called_once()

    @patch.object(sync_job_catalog, "JOB_INGESTION_POLL_SECONDS", 60)
    @patch.object(sync_job_catalog.time, "sleep", side_effect=KeyboardInterrupt)
    @patch.object(
        sync_job_catalog,
        "run_once",
        side_effect=RuntimeError("sensitive-provider-token"),
    )
    @patch.object(
        sys,
        "argv",
        ["sync_job_catalog", "--watch"],
    )
    def test_watch_mode_retries_cycle_failures_without_logging_secret(
        self,
        run_once,
        sleep,
    ):
        with (
            patch.object(sync_job_catalog.logger, "warning") as warning,
            patch.object(sync_job_catalog.logger, "info") as info,
        ):
            sync_job_catalog.main()

        run_once.assert_called_once_with(force=False)
        sleep.assert_called_once_with(60)
        logged_values = " ".join(map(str, warning.call_args.args))
        self.assertNotIn("sensitive-provider-token", logged_values)
        info.assert_called_once_with("Job ingestion worker stopped.")


if __name__ == "__main__":
    unittest.main()
