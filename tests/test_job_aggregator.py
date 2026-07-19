import unittest
from unittest.mock import patch

from backend.services.job_aggregator import _listing_url, aggregate_jobs


class JobAggregatorTests(unittest.TestCase):
    def test_normalizes_direct_provider_listing_url(self):
        self.assertEqual(
            _listing_url({"url": "https://jobs.example.com/roles/123"}),
            "https://jobs.example.com/roles/123",
        )
        self.assertEqual(
            _listing_url({"redirect_url": "https://provider.example/job/456"}),
            "https://provider.example/job/456",
        )

    def test_rejects_unsafe_or_relative_listing_url(self):
        self.assertEqual(_listing_url({"url": "javascript:alert(1)"}), "")
        self.assertEqual(_listing_url({"url": "/jobs/123"}), "")

    @patch("backend.services.job_aggregator.adzuna_search", return_value=[])
    @patch("backend.services.job_aggregator.arbeitnow_search", return_value=[])
    @patch("backend.services.job_aggregator.remoteok_search", return_value=[])
    @patch("backend.services.job_aggregator.himalayas_search")
    @patch("backend.services.job_aggregator.jooble_search")
    def test_blends_large_provider_results(
        self,
        jooble_search,
        himalayas_search,
        _remoteok_search,
        _arbeitnow_search,
        _adzuna_search,
    ):
        jooble_search.return_value = [
            {"title": f"Jooble {index}", "company": "J"}
            for index in range(20)
        ]
        himalayas_search.return_value = [
            {"title": f"Himalayas {index}", "company": "H"}
            for index in range(20)
        ]

        jobs = aggregate_jobs("Engineer", "Worldwide", results=20)

        self.assertEqual(len(jobs), 20)
        self.assertEqual(
            {job["source"] for job in jobs},
            {"Jooble", "Himalayas"},
        )
        statuses = {item["name"]: item for item in jobs.provider_status}
        self.assertEqual(statuses["Jooble"]["status"], "active")
        self.assertEqual(statuses["Himalayas"]["count"], 20)
        self.assertEqual(jobs[0]["source_homepage"], "https://jooble.org/")
        self.assertIn("api_page", statuses["Jooble"])

    @patch("backend.services.job_aggregator.adzuna_search", return_value=[])
    @patch("backend.services.job_aggregator.arbeitnow_search", return_value=[])
    @patch("backend.services.job_aggregator.remoteok_search", return_value=[])
    @patch("backend.services.job_aggregator.himalayas_search", return_value=[])
    @patch(
        "backend.services.job_aggregator.jooble_search",
        side_effect=RuntimeError("timeout"),
    )
    def test_provider_failure_does_not_break_other_sources(
        self,
        _jooble_search,
        _himalayas_search,
        _remoteok_search,
        _arbeitnow_search,
        _adzuna_search,
    ):
        jobs = aggregate_jobs("Engineer", "Worldwide")

        statuses = {item["name"]: item for item in jobs.provider_status}
        self.assertEqual(jobs, [])
        self.assertEqual(statuses["Jooble"]["status"], "unavailable")
        self.assertEqual(statuses["Himalayas"]["status"], "no_results")


if __name__ == "__main__":
    unittest.main()
