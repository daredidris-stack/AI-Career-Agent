import unittest
from unittest.mock import Mock, patch

from himalayas_api import search_jobs


class HimalayasApiTests(unittest.TestCase):
    @patch("himalayas_api.requests.get")
    def test_searches_by_country_and_normalizes_results(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "title": "Cloud Engineer",
                "companyName": "Example Inc",
                "locationRestrictions": [{"name": "Mexico"}],
                "description": "<p>Build AWS platforms</p>",
                "categories": ["AWS", "Terraform"],
                "applicationLink": "https://example.com/apply",
                "employmentType": "Full Time",
                "minSalary": 80000,
                "maxSalary": 100000,
                "currency": "USD",
                "salaryPeriod": "annual",
                "pubDate": 123,
            }]
        }
        mock_get.return_value = response

        jobs = search_jobs("Cloud Engineer", "Mexico City, Mexico", 2)

        self.assertEqual(mock_get.call_args.kwargs["params"]["country"], "Mexico")
        self.assertEqual(mock_get.call_args.kwargs["params"]["page"], 2)
        self.assertEqual(jobs[0]["company"], "Example Inc")
        self.assertEqual(jobs[0]["description"], "Build AWS platforms")
        self.assertEqual(jobs[0]["salary"], "USD 80,000 - 100,000 per annual")
        response.raise_for_status.assert_called_once()

    @patch("himalayas_api.requests.get")
    def test_worldwide_search_requests_worldwide_jobs(self, mock_get):
        response = Mock()
        response.json.return_value = {"jobs": []}
        mock_get.return_value = response

        search_jobs("SRE", "Worldwide")

        params = mock_get.call_args.kwargs["params"]
        self.assertTrue(params["worldwide"])
        self.assertNotIn("country", params)

    @patch("himalayas_api.requests.get")
    def test_normalizes_string_location_restrictions(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "title": "Site Reliability Engineer",
                "locationRestrictions": ["Worldwide", "Mexico"],
            }]
        }
        mock_get.return_value = response

        jobs = search_jobs("SRE", "Worldwide")

        self.assertEqual(jobs[0]["location"], "Worldwide, Mexico")

    @patch("himalayas_api.requests.get")
    def test_ignores_malformed_location_restrictions(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "title": "Site Reliability Engineer",
                "locationRestrictions": [None, 42, {}, ""],
            }]
        }
        mock_get.return_value = response

        jobs = search_jobs("SRE", "Worldwide")

        self.assertEqual(jobs[0]["location"], "Worldwide remote")


if __name__ == "__main__":
    unittest.main()
