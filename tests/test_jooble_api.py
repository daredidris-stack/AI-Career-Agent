import unittest
from unittest.mock import Mock, patch

import requests

from jooble_api import search_jobs


class JoobleApiTests(unittest.TestCase):
    @patch("jooble_api.JOOBLE_API_KEY", "test-key")
    @patch("jooble_api.requests.post")
    def test_searches_with_pagination_and_normalizes_results(
        self,
        mock_post,
    ):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "title": "Cloud Engineer",
                "company": "Example Inc",
                "location": "Mexico",
                "snippet": "AWS role",
                "link": "https://example.com/job",
                "type": "Full-time",
                "salary": "Competitive",
            }]
        }
        mock_post.return_value = response

        jobs = search_jobs("Cloud Engineer", "Worldwide", 2, 25)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Example Inc")
        payload = mock_post.call_args.kwargs["json"]
        self.assertEqual(payload["location"], "")
        self.assertEqual(payload["page"], 2)
        self.assertEqual(payload["ResultOnPage"], 25)
        response.raise_for_status.assert_called_once()

    @patch("jooble_api.JOOBLE_API_KEY", None)
    def test_missing_key_returns_empty_fallback(self):
        self.assertEqual(search_jobs("Engineer"), [])

    @patch("jooble_api.JOOBLE_API_KEY", "sensitive-test-key")
    @patch("jooble_api.requests.post")
    def test_request_errors_do_not_expose_api_key(self, mock_post):
        mock_post.side_effect = requests.ConnectionError(
            "failed https://jooble.org/api/sensitive-test-key"
        )

        with self.assertRaises(RuntimeError) as context:
            search_jobs("Engineer")

        self.assertEqual(str(context.exception), "Jooble request failed.")
        self.assertNotIn("sensitive-test-key", str(context.exception))

    @patch("jooble_api.JOOBLE_API_KEY", "test-key")
    @patch("jooble_api.requests.post")
    def test_invalid_json_is_reported_as_provider_failure(self, mock_post):
        response = Mock()
        response.json.side_effect = ValueError("invalid json")
        mock_post.return_value = response

        with self.assertRaisesRegex(RuntimeError, "Jooble request failed"):
            search_jobs("Engineer")


if __name__ == "__main__":
    unittest.main()
