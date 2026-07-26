import unittest
from unittest.mock import Mock, patch

import requests

from adzuna_api import search_jobs


class AdzunaApiTests(unittest.TestCase):
    def setUp(self):
        self.response = Mock(status_code=200)
        self.response.json.return_value = {"results": []}

    @patch("adzuna_api.ADZUNA_APP_ID", "test-id")
    @patch("adzuna_api.ADZUNA_APP_KEY", "test-key")
    @patch("adzuna_api.ADZUNA_WORLDWIDE_MARKETS", ["mx", "us"])
    @patch("adzuna_api.requests.get")
    def test_worldwide_search_uses_multiple_markets_without_location_filter(
        self,
        mock_get,
    ):
        mock_get.return_value = self.response

        search_jobs("Software Engineer", "Worldwide", 50)

        self.assertEqual(mock_get.call_count, 2)
        called_urls = {call.args[0] for call in mock_get.call_args_list}
        self.assertEqual(called_urls, {
            "https://api.adzuna.com/v1/api/jobs/mx/search/1",
            "https://api.adzuna.com/v1/api/jobs/us/search/1",
        })
        for call in mock_get.call_args_list:
            params = call.kwargs["params"]
            self.assertNotIn("where", params)
            self.assertEqual(params["results_per_page"], 25)

    @patch("adzuna_api.ADZUNA_APP_ID", "test-id")
    @patch("adzuna_api.ADZUNA_APP_KEY", "test-key")
    @patch("adzuna_api.requests.get")
    def test_specific_location_is_forwarded(self, mock_get):
        mock_get.return_value = self.response

        search_jobs("Software Engineer", "Monterrey, Mexico", 25)

        params = mock_get.call_args.kwargs["params"]
        self.assertIn("/mx/", mock_get.call_args.args[0])
        self.assertEqual(params["where"], "Monterrey, Mexico")
        self.assertEqual(params["results_per_page"], 25)

    @patch("adzuna_api.ADZUNA_APP_ID", "test-id")
    @patch("adzuna_api.ADZUNA_APP_KEY", "test-key")
    @patch("adzuna_api.ADZUNA_WORLDWIDE_MARKETS", ["mx", "us"])
    @patch("adzuna_api.requests.get")
    def test_worldwide_search_keeps_available_markets(self, mock_get):
        mock_get.side_effect = [
            requests.ConnectionError("one market failed"),
            self.response,
        ]

        jobs = search_jobs("Software Engineer", "Worldwide", 50)

        self.assertEqual(jobs, [])
        self.assertEqual(mock_get.call_count, 2)

    @patch("adzuna_api.ADZUNA_APP_ID", "sensitive-id")
    @patch("adzuna_api.ADZUNA_APP_KEY", "sensitive-key")
    @patch("adzuna_api.ADZUNA_WORLDWIDE_MARKETS", ["mx"])
    @patch("adzuna_api.requests.get")
    def test_request_errors_do_not_expose_api_credentials(self, mock_get):
        mock_get.side_effect = requests.ConnectionError(
            "failed request containing sensitive-id and sensitive-key"
        )

        with self.assertRaises(RuntimeError) as context:
            search_jobs("Engineer")

        self.assertEqual(str(context.exception), "Adzuna request failed.")
        self.assertNotIn("sensitive", str(context.exception))


if __name__ == "__main__":
    unittest.main()
