import unittest
from unittest.mock import patch

from backend.services.job_aggregator import aggregate_jobs


class JobAggregatorTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
