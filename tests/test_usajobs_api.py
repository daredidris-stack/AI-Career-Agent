import unittest
from unittest.mock import Mock, patch

from usajobs_api import search_jobs


class UsaJobsApiTests(unittest.TestCase):
    @patch("usajobs_api.USAJOBS_USER_AGENT", "developer@example.com")
    @patch("usajobs_api.USAJOBS_API_KEY", "test-key")
    @patch("usajobs_api.requests.get")
    def test_returns_full_government_job(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "SearchResult": {
                "SearchResultItems": [{
                    "MatchedObjectId": "123",
                    "MatchedObjectDescriptor": {
                        "PositionID": "ABC-123",
                        "PositionTitle": "IT Specialist",
                        "PositionURI": "https://www.usajobs.gov/job/123",
                        "ApplyURI": ["https://www.usajobs.gov/job/123/apply"],
                        "PositionLocationDisplay": "Remote",
                        "OrganizationName": "Department of Example",
                        "JobCategory": [{"Name": "Information Technology"}],
                        "PositionSchedule": [{"Name": "Full Time"}],
                        "PositionOfferingType": [{"Name": "Permanent"}],
                        "QualificationSummary": "Three years of experience.",
                        "PositionRemuneration": [{
                            "MinimumRange": "80000",
                            "MaximumRange": "110000",
                            "RateIntervalCode": "PA",
                            "Description": "Per Year",
                        }],
                        "PublicationStartDate": "2026-07-20T00:00:00Z",
                        "UserArea": {"Details": {
                            "JobSummary": "Support critical systems.",
                            "MajorDuties": "Operate infrastructure.",
                            "Requirements": "Public trust clearance.",
                        }},
                    },
                }],
            },
        }
        mock_get.return_value = response

        jobs = search_jobs("IT Specialist", "Remote", page=2, results=25)

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["salary_min"], 80000)
        self.assertIn("Duties", jobs[0]["description"])
        self.assertTrue(jobs[0]["url"].endswith("/apply"))
        request = mock_get.call_args.kwargs
        self.assertEqual(request["headers"]["Authorization-Key"], "test-key")
        self.assertEqual(request["headers"]["User-Agent"], "developer@example.com")
        self.assertEqual(request["params"]["RemoteIndicator"], "True")
        self.assertEqual(request["params"]["Page"], 2)

    @patch("usajobs_api.USAJOBS_USER_AGENT", "")
    @patch("usajobs_api.USAJOBS_API_KEY", "")
    @patch("usajobs_api.requests.get")
    def test_missing_credentials_disable_provider(self, mock_get):
        self.assertEqual(search_jobs("Engineer"), [])
        mock_get.assert_not_called()


if __name__ == "__main__":
    unittest.main()
