import unittest
from unittest.mock import Mock, patch

import fantastic_jobs_api
from fantastic_jobs_api import search_jobs


class FantasticJobsApiTests(unittest.TestCase):
    def setUp(self):
        fantastic_jobs_api._CACHE.clear()

    @patch("fantastic_jobs_api.FANTASTIC_JOBS_API_KEY", "test-key")
    @patch("fantastic_jobs_api.FANTASTIC_JOBS_MAX_RESULTS", 20)
    @patch("fantastic_jobs_api.requests.get")
    def test_normalizes_full_job_and_caches_identical_search(self, mock_get):
        response = Mock()
        response.json.return_value = [{
            "id": 4821,
            "title": "Infrastructure Engineer",
            "organization": "Example Systems",
            "url": "https://example.com/jobs/4821",
            "date_posted": "2026-07-21T10:00:00Z",
            "date_valid_through": "2026-08-21T10:00:00Z",
            "locations_derived": ["Mexico City, Mexico"],
            "description_text": "Complete infrastructure job description.",
            "ai_employment_type": ["FULL_TIME"],
            "ai_work_arrangement": "Hybrid",
            "ai_key_skills": ["Linux", "Networking"],
            "ai_salary_currency": "USD",
            "ai_salary_min_value": 90000,
            "ai_salary_max_value": 120000,
            "ai_salary_unit_text": "YEAR",
            "ai_visa_sponsorship": True,
        }]
        mock_get.return_value = response

        first = search_jobs(
            "Infrastructure Engineer",
            "Mexico",
            page=2,
            results=50,
        )
        second = search_jobs(
            "Infrastructure Engineer",
            "Mexico",
            page=2,
            results=50,
        )

        self.assertEqual(first, second)
        self.assertEqual(first[0]["company"], "Example Systems")
        self.assertEqual(
            first[0]["description"],
            "Complete infrastructure job description.",
        )
        self.assertEqual(first[0]["salary_min"], 90000)
        self.assertEqual(first[0]["job_type"], "Full Time")
        self.assertTrue(first[0]["visa_sponsorship"])
        request = mock_get.call_args.kwargs
        self.assertEqual(request["headers"]["Authorization"], "Bearer test-key")
        self.assertEqual(request["params"]["description_format"], "text")
        self.assertEqual(request["params"]["time_frame"], "6m")
        self.assertEqual(request["params"]["limit"], 20)
        self.assertEqual(request["params"]["offset"], 20)
        self.assertEqual(request["params"]["location"], "Mexico")
        mock_get.assert_called_once()

    @patch("fantastic_jobs_api.FANTASTIC_JOBS_API_KEY", "test-key")
    @patch("fantastic_jobs_api.requests.get")
    def test_remote_search_uses_normalized_arrangement_filter(self, mock_get):
        response = Mock()
        response.json.return_value = []
        mock_get.return_value = response

        self.assertEqual(search_jobs("Writer", "Remote"), [])

        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(
            params["ai_work_arrangement"],
            "Remote Solely,Remote OK",
        )
        self.assertNotIn("location", params)

    @patch("fantastic_jobs_api.FANTASTIC_JOBS_API_KEY", "")
    @patch("fantastic_jobs_api.requests.get")
    def test_missing_key_disables_provider(self, mock_get):
        self.assertEqual(search_jobs("Engineer"), [])
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
