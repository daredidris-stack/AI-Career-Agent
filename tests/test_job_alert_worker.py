import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.job_alert_worker import JobAlertWorker


class JobAlertWorkerTests(unittest.TestCase):
    def setUp(self):
        self.library = Mock()
        self.library.repository = Mock()
        self.search = Mock()
        self.alerts = Mock()
        self.alerts.available = True
        self.saved_search = SimpleNamespace(
            id=4,
            last_run_at=object(),
        )
        self.user = SimpleNamespace(id=7)
        self.library.repository.list_due_searches.return_value = [
            (self.saved_search, self.user),
        ]
        self.library.search_filters.return_value = {
            "keyword": "Platform Engineer",
        }

    def test_unavailable_worker_exits_without_querying(self):
        self.alerts.available = False

        report = JobAlertWorker(
            self.library,
            self.search,
            self.alerts,
        ).run_due()

        self.assertFalse(report["configured"])
        self.library.repository.list_due_searches.assert_not_called()

    def test_successful_send_records_results_and_completes_schedule(self):
        jobs = [{"title": "Platform Engineer"}]
        self.search.search_for_user.return_value = {"jobs": jobs}
        self.library.new_jobs.return_value = jobs
        self.alerts.send_matches.return_value = True

        report = JobAlertWorker(
            self.library,
            self.search,
            self.alerts,
        ).run_due()

        self.assertEqual(report["sent"], 1)
        self.library.record_search_results.assert_called_once_with(
            self.saved_search,
            jobs,
        )
        self.alerts.complete_search.assert_called_once_with(self.saved_search)

    def test_failed_send_does_not_mark_jobs_seen(self):
        jobs = [{"title": "Platform Engineer"}]
        self.search.search_for_user.return_value = {"jobs": jobs}
        self.library.new_jobs.return_value = jobs
        self.alerts.send_matches.return_value = False

        report = JobAlertWorker(
            self.library,
            self.search,
            self.alerts,
        ).run_due()

        self.assertEqual(report["failed"], 1)
        self.library.record_search_results.assert_not_called()
        self.alerts.complete_search.assert_not_called()

    def test_first_run_establishes_baseline_without_email(self):
        self.saved_search.last_run_at = None
        jobs = [{"title": "Platform Engineer"}]
        self.search.search_for_user.return_value = {"jobs": jobs}
        self.library.new_jobs.return_value = []

        report = JobAlertWorker(
            self.library,
            self.search,
            self.alerts,
        ).run_due()

        self.assertEqual(report["baselined"], 1)
        self.alerts.send_matches.assert_not_called()
        self.library.record_search_results.assert_called_once()


if __name__ == "__main__":
    unittest.main()
