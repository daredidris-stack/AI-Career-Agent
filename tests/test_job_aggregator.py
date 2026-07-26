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

    @patch.multiple(
        "backend.services.job_aggregator",
        ADZUNA_APP_ID="test-id",
        ADZUNA_APP_KEY="test-key",
        ASHBY_JOB_BOARDS=["Example|example"],
        DIRECT_EMPLOYER_JOB_SOURCES={"microsoft", "apple", "crossover"},
        FANTASTIC_JOBS_API_KEY="test-key",
        GREENHOUSE_JOB_BOARDS=["Example|example"],
        JOOBLE_API_KEY="test-key",
        LEVER_JOB_SITES=["Example|example"],
        SERPAPI_API_KEY="test-key",
        THEIRSTACK_API_KEY="test-key",
        USAJOBS_API_KEY="test-key",
        USAJOBS_USER_AGENT="test@example.com",
    )
    @patch("backend.services.job_aggregator.fantastic_search", return_value=[])
    @patch("backend.services.job_aggregator.serpapi_search", return_value=[])
    @patch("backend.services.job_aggregator.usajobs_search", return_value=[])
    @patch("backend.services.job_aggregator.ashby_search", return_value=[])
    @patch("backend.services.job_aggregator.lever_search", return_value=[])
    @patch("backend.services.job_aggregator.greenhouse_search", return_value=[])
    @patch("backend.services.job_aggregator.theirstack_search", return_value=[])
    @patch("backend.services.job_aggregator.crossover_search", return_value=[])
    @patch("backend.services.job_aggregator.apple_search", return_value=[])
    @patch("backend.services.job_aggregator.microsoft_search", return_value=[])
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
        _microsoft_search,
        _apple_search,
        _crossover_search,
        _theirstack_search,
        _greenhouse_search,
        _lever_search,
        _ashby_search,
        _usajobs_search,
        _serpapi_search,
        _fantastic_search,
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
        _arbeitnow_search.assert_called_once_with(
            "Engineer", "Worldwide", "", 20
        )
        _adzuna_search.assert_called_once_with(
            "Engineer", "Worldwide", 20
        )
        _microsoft_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _apple_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _crossover_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _theirstack_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _greenhouse_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _lever_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _ashby_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _usajobs_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _serpapi_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )
        _fantastic_search.assert_called_once_with(
            "Engineer", "Worldwide", 1, 20
        )

    @patch.multiple(
        "backend.services.job_aggregator",
        ADZUNA_APP_ID="test-id",
        ADZUNA_APP_KEY="test-key",
        ASHBY_JOB_BOARDS=["Example|example"],
        DIRECT_EMPLOYER_JOB_SOURCES={"microsoft", "apple", "crossover"},
        FANTASTIC_JOBS_API_KEY="test-key",
        GREENHOUSE_JOB_BOARDS=["Example|example"],
        JOOBLE_API_KEY="test-key",
        LEVER_JOB_SITES=["Example|example"],
        SERPAPI_API_KEY="test-key",
        THEIRSTACK_API_KEY="test-key",
        USAJOBS_API_KEY="test-key",
        USAJOBS_USER_AGENT="test@example.com",
    )
    @patch("backend.services.job_aggregator.fantastic_search", return_value=[])
    @patch("backend.services.job_aggregator.serpapi_search", return_value=[])
    @patch("backend.services.job_aggregator.usajobs_search", return_value=[])
    @patch("backend.services.job_aggregator.ashby_search", return_value=[])
    @patch("backend.services.job_aggregator.lever_search", return_value=[])
    @patch("backend.services.job_aggregator.greenhouse_search", return_value=[])
    @patch("backend.services.job_aggregator.theirstack_search", return_value=[])
    @patch("backend.services.job_aggregator.crossover_search", return_value=[])
    @patch("backend.services.job_aggregator.apple_search", return_value=[])
    @patch("backend.services.job_aggregator.microsoft_search", return_value=[])
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
        _microsoft_search,
        _apple_search,
        _crossover_search,
        _theirstack_search,
        _greenhouse_search,
        _lever_search,
        _ashby_search,
        _usajobs_search,
        _serpapi_search,
        _fantastic_search,
    ):
        jobs = aggregate_jobs("Engineer", "Worldwide")

        statuses = {item["name"]: item for item in jobs.provider_status}
        self.assertEqual(jobs, [])
        self.assertEqual(statuses["Jooble"]["status"], "unavailable")
        self.assertEqual(statuses["Himalayas"]["status"], "no_results")

    @patch.multiple(
        "backend.services.job_aggregator",
        ASHBY_JOB_BOARDS=[],
        DIRECT_EMPLOYER_JOB_SOURCES=set(),
        FANTASTIC_JOBS_API_KEY="",
        GREENHOUSE_JOB_BOARDS=[],
        JOOBLE_API_KEY="",
        LEVER_JOB_SITES=[],
        SERPAPI_API_KEY="",
        THEIRSTACK_API_KEY="",
        USAJOBS_API_KEY="",
        USAJOBS_USER_AGENT="",
    )
    @patch("backend.services.job_aggregator.crossover_search")
    @patch("backend.services.job_aggregator.apple_search")
    @patch("backend.services.job_aggregator.microsoft_search")
    @patch("backend.services.job_aggregator.himalayas_search", return_value=[])
    def test_unconfigured_providers_are_not_called(
        self,
        _himalayas_search,
        microsoft_search,
        apple_search,
        crossover_search,
    ):
        jobs = aggregate_jobs("Engineer", "Worldwide", page=2)

        statuses = {item["name"]: item for item in jobs.provider_status}
        self.assertEqual(statuses["Microsoft"]["status"], "not_configured")
        self.assertEqual(statuses["Apple"]["status"], "not_configured")
        self.assertEqual(statuses["Crossover"]["status"], "not_configured")
        microsoft_search.assert_not_called()
        apple_search.assert_not_called()
        crossover_search.assert_not_called()


if __name__ == "__main__":
    unittest.main()
