import unittest
from unittest.mock import Mock, patch

from ats_job_apis import (
    search_ashby_jobs,
    search_greenhouse_jobs,
    search_lever_jobs,
)


class AtsJobApiTests(unittest.TestCase):
    @patch("ats_job_apis.GREENHOUSE_JOB_BOARDS", ["Acme Corp|acme"])
    @patch("ats_job_apis.requests.get")
    def test_greenhouse_returns_full_normalized_jobs(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "id": 123,
                "title": "Platform Engineer",
                "location": {"name": "Madrid, Spain"},
                "content": "<p>Build reliable systems.</p>",
                "absolute_url": "https://boards.greenhouse.io/acme/jobs/123",
                "updated_at": "2026-07-20T12:00:00Z",
            }]
        }
        mock_get.return_value = response

        jobs = search_greenhouse_jobs("Platform Engineer", "Worldwide")

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Acme Corp")
        self.assertEqual(jobs[0]["description"], "Build reliable systems.")
        self.assertEqual(
            mock_get.call_args.kwargs["params"],
            {"content": "true"},
        )

    @patch("ats_job_apis.LEVER_JOB_SITES", ["Example Labs|example"])
    @patch("ats_job_apis.requests.get")
    def test_lever_returns_description_and_apply_url(self, mock_get):
        response = Mock()
        response.json.return_value = [{
            "id": "posting-1",
            "text": "Product Manager",
            "categories": {
                "location": "Remote",
                "allLocations": ["Remote"],
                "commitment": "Full-time",
            },
            "descriptionPlain": "Own the product roadmap.",
            "hostedUrl": "https://jobs.lever.co/example/posting-1",
            "applyUrl": "https://jobs.lever.co/example/posting-1/apply",
            "workplaceType": "remote",
            "salaryRange": {
                "min": 100000,
                "max": 140000,
                "interval": "year",
            },
            "salaryDescriptionPlain": "$100K-$140K",
        }]
        mock_get.return_value = response

        jobs = search_lever_jobs("Product Manager", "Remote")

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Example Labs")
        self.assertEqual(jobs[0]["salary_min"], 100000)
        self.assertTrue(jobs[0]["apply_url"].endswith("/apply"))

    @patch("ats_job_apis.ASHBY_JOB_BOARDS", ["Example AI|example-ai"])
    @patch("ats_job_apis.requests.get")
    def test_ashby_returns_compensation_and_full_description(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "title": "Data Engineer",
                "location": "Mexico",
                "isListed": True,
                "isRemote": True,
                "workplaceType": "Remote",
                "descriptionPlain": "Build worldwide data pipelines.",
                "publishedAt": "2026-07-19T10:00:00Z",
                "employmentType": "FullTime",
                "jobUrl": "https://jobs.ashbyhq.com/example-ai/job-1",
                "applyUrl": "https://jobs.ashbyhq.com/example-ai/job-1/apply",
                "compensation": {
                    "scrapeableCompensationSalarySummary": "$90K - $120K",
                    "summaryComponents": [{
                        "compensationType": "Salary",
                        "interval": "1 YEAR",
                        "minValue": 90000,
                        "maxValue": 120000,
                    }],
                },
            }]
        }
        mock_get.return_value = response

        jobs = search_ashby_jobs("Data Engineer", "Worldwide")

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["job_type"], "Full Time")
        self.assertEqual(jobs[0]["salary_max"], 120000)
        self.assertEqual(
            mock_get.call_args.kwargs["params"],
            {"includeCompensation": "true"},
        )


if __name__ == "__main__":
    unittest.main()
