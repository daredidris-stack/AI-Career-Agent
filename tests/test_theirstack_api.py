import unittest
from unittest.mock import Mock, patch

import requests

from theirstack_api import search_jobs


class TheirStackApiTests(unittest.TestCase):
    @patch("theirstack_api.THEIRSTACK_API_KEY", "test-key")
    @patch("theirstack_api.requests.post")
    def test_returns_full_worldwide_job_records(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "data": [{
                "job_title": "Data Center Technician",
                "company": "IBM",
                "short_location": "Madrid, Spain",
                "description": "Complete role description",
                "technology_slugs": ["linux"],
                "final_url": "https://careers.ibm.com/job/123",
                "employment_statuses": ["full_time"],
                "salary_string": "$50,000 - $60,000",
                "min_annual_salary_usd": 50000,
                "max_annual_salary_usd": 60000,
                "date_posted": "2026-07-19",
            }]
        }
        mock_post.return_value = response

        jobs = search_jobs(
            "Data Center Technician", "Worldwide", page=2, results=25
        )

        self.assertEqual(jobs[0]["company"], "IBM")
        self.assertEqual(jobs[0]["description"], "Complete role description")
        self.assertEqual(jobs[0]["job_type"], "Full Time")
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["limit"], 25)
        self.assertEqual(payload["posted_at_max_age_days"], 30)
        self.assertIn("critical facilities technician", payload["job_title_or"])
        self.assertNotIn("job_country_code_or", payload)
        self.assertEqual(
            mock_post.call_args.kwargs["headers"]["Authorization"],
            "Bearer test-key",
        )

    @patch("theirstack_api.THEIRSTACK_API_KEY", "test-key")
    @patch("theirstack_api.requests.post")
    def test_filters_specific_country_and_city(self, mock_post):
        response = Mock()
        response.json.return_value = {"data": []}
        mock_post.return_value = response

        search_jobs("Engineer", "Monterrey, Mexico", results=10)

        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["job_country_code_or"], ["MX"])
        self.assertEqual(payload["job_location_pattern_or"], ["Monterrey"])

    @patch("theirstack_api.THEIRSTACK_API_KEY", "sensitive-key")
    @patch("theirstack_api.requests.post")
    def test_request_error_does_not_expose_key(self, mock_post):
        mock_post.side_effect = requests.ConnectionError(
            "request included sensitive-key"
        )

        with self.assertRaises(RuntimeError) as context:
            search_jobs("Engineer")

        self.assertEqual(
            str(context.exception),
            "Worldwide job index request failed.",
        )
        self.assertNotIn("sensitive", str(context.exception))


if __name__ == "__main__":
    unittest.main()
