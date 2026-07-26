import unittest
from unittest.mock import Mock, patch

from employer_job_apis import (
    search_apple_jobs,
    search_crossover_jobs,
    search_microsoft_jobs,
)


class EmployerJobApiTests(unittest.TestCase):
    @patch("employer_job_apis.requests.get")
    def test_normalizes_microsoft_careers_results(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "data": {
                "positions": [{
                    "id": 123,
                    "name": "Data Center Technician",
                    "locations": ["Mexico, Queretaro"],
                    "postedTs": 1784536040,
                    "workLocationOption": "onsite",
                    "positionUrl": "/careers/job/123",
                }]
            }
        }
        mock_get.return_value = response

        jobs = search_microsoft_jobs(
            "Data Center Technician", "Worldwide", page=2, results=20
        )

        self.assertEqual(jobs[0]["company"], "Microsoft")
        self.assertEqual(jobs[0]["location"], "Mexico, Queretaro")
        self.assertEqual(
            jobs[0]["url"],
            "https://apply.careers.microsoft.com/careers/job/123?hl=en",
        )
        params = mock_get.call_args.kwargs["params"]
        self.assertEqual(params["start"], 10)
        self.assertEqual(params["location"], "")

    @patch("employer_job_apis.requests.post")
    def test_normalizes_apple_search_results(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "res": {
                "searchResults": [{
                    "id": "200659430-6709",
                    "postingTitle": "Critical Facilities Technician",
                    "jobSummary": "Operate critical infrastructure.",
                    "locations": [{
                        "name": "Waukee",
                        "stateProvince": "Iowa",
                        "countryName": "United States of America",
                    }],
                    "postDateInGMT": "2026-04-23T03:57:39.203Z",
                    "transformedPostingTitle": "critical-facilities-technician",
                    "homeOffice": False,
                }]
            }
        }
        mock_post.return_value = response

        jobs = search_apple_jobs(
            "Data Center Technician", "Worldwide", results=10
        )

        self.assertEqual(jobs[0]["company"], "Apple")
        self.assertEqual(
            jobs[0]["location"],
            "Waukee, Iowa, United States of America",
        )
        self.assertEqual(
            jobs[0]["url"],
            "https://jobs.apple.com/en-us/details/"
            "200659430-6709/critical-facilities-technician",
        )
        self.assertEqual(
            mock_post.call_args.kwargs["json"]["query"],
            "Data Center Technician",
        )

    @patch("employer_job_apis.requests.get")
    def test_filters_and_normalizes_crossover_results(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "records": [{
                "Name": "Data Center Operations Technician",
                "Brand__r": {"Name": "Trilogy"},
                "DisplayUrl": "https://www.crossover.com/jobs/123/trilogy/tech",
                "Geographic_Restriction__c": "Global",
                "Is_InPerson__c": False,
                "Yearly_Rate__c": 60000,
                "Hourly_Rate__c": 30,
                "Job_Type__c": "full-time",
            }, {
                "Name": "Account Executive",
                "Brand__r": {"Name": "Trilogy"},
            }]
        }
        mock_get.return_value = response

        jobs = search_crossover_jobs(
            "Data Center Technician", "Worldwide", results=10
        )

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Trilogy")
        self.assertEqual(jobs[0]["location"], "Worldwide remote")
        self.assertEqual(jobs[0]["salary"], "$60,000/year USD")


if __name__ == "__main__":
    unittest.main()
