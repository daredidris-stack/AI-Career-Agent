import unittest
from unittest.mock import Mock, patch

import serpapi_jobs
from serpapi_jobs import search_jobs


class SerpApiJobsTests(unittest.TestCase):
    def setUp(self):
        serpapi_jobs._PAGE_TOKENS.clear()

    @patch("serpapi_jobs.SERPAPI_API_KEY", "test-key")
    @patch("serpapi_jobs.requests.get")
    def test_normalizes_google_jobs_and_stores_page_token(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs_results": [{
                "job_id": "google-job-1",
                "title": "Cloud Engineer",
                "company_name": "Example Cloud",
                "location": "London, UK",
                "description": "Complete cloud engineering description.",
                "apply_options": [{
                    "title": "Employer",
                    "link": "https://example.com/jobs/1",
                }],
                "detected_extensions": {
                    "posted_at": "2 days ago",
                    "schedule_type": "Full-time",
                    "salary": "$100K-$120K",
                },
            }],
            "serpapi_pagination": {"next_page_token": "page-two"},
        }
        mock_get.return_value = response

        jobs = search_jobs("Cloud Engineer", "London, UK", results=50)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Example Cloud")
        self.assertEqual(jobs[0]["description"], "Complete cloud engineering description.")
        self.assertEqual(jobs[0]["url"], "https://example.com/jobs/1")
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["engine"], "google_jobs")
        self.assertEqual(params["location"], "London, UK")
        self.assertEqual(params["api_key"], "test-key")

        response.json.return_value = {"jobs_results": []}
        search_jobs("Cloud Engineer", "London, UK", page=2)
        self.assertEqual(
            mock_get.call_args.kwargs["params"]["next_page_token"],
            "page-two",
        )

    @patch("serpapi_jobs.SERPAPI_API_KEY", "test-key")
    @patch("serpapi_jobs.requests.get")
    def test_page_without_cached_token_does_not_spend_credit(self, mock_get):
        self.assertEqual(search_jobs("Engineer", page=2), [])
        mock_get.assert_not_called()

    @patch("serpapi_jobs.SERPAPI_API_KEY", "test-key")
    @patch("serpapi_jobs.requests.get")
    def test_google_no_results_response_is_not_a_provider_failure(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "error": "Google hasn't returned any results for this query.",
            "search_metadata": {"status": "Success"},
        }
        mock_get.return_value = response

        self.assertEqual(search_jobs("Unmatched role"), [])


if __name__ == "__main__":
    unittest.main()
