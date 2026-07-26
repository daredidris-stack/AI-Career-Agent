import json
import unittest
from unittest.mock import Mock, patch

import requests

from backend.services.job_description_service import JobDescriptionService


class JobDescriptionServiceTests(unittest.TestCase):
    @patch("backend.services.job_description_service.requests.get")
    def test_uses_microsoft_public_detail_api(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "data": {
                "jobDescription": (
                    "<b>Overview</b><p>Operate Microsoft infrastructure.</p>"
                    "<b>Qualifications</b><ul><li>Networking</li></ul>"
                )
            }
        }
        mock_get.return_value = response

        description = JobDescriptionService().enrich(
            "Data Center Technician",
            "Microsoft",
            listing_url=(
                "https://apply.careers.microsoft.com/careers/job/123?hl=en"
            ),
        )

        self.assertIn("Operate Microsoft infrastructure.", description)
        self.assertIn("- Networking", description)
        self.assertEqual(
            mock_get.call_args.args[0],
            "https://apply.careers.microsoft.com/api/pcsx/position_details",
        )
        self.assertEqual(
            mock_get.call_args.kwargs["params"]["position_id"],
            "123",
        )

    @patch("backend.services.job_description_service.requests.get")
    def test_extracts_complete_apple_description_from_job_page(self, mock_get):
        payload = {
            "loaderData": {
                "jobDetails": {
                    "jobsData": {
                        "jobSummary": "Apple summary",
                        "description": "Complete Apple responsibilities",
                        "minimumQualifications": "Linux\nNetworking",
                        "preferredQualifications": "Data center experience",
                    }
                }
            }
        }
        encoded = json.dumps(json.dumps(payload))
        response = Mock()
        response.text = (
            "<script>window.__staticRouterHydrationData = "
            f"JSON.parse({encoded});</script>"
        )
        mock_get.return_value = response

        description = JobDescriptionService().enrich(
            "Critical Facilities Technician",
            "Apple",
            listing_url=(
                "https://jobs.apple.com/en-us/details/123/apple-technician"
            ),
        )

        self.assertIn("Summary\nApple summary", description)
        self.assertIn(
            "Description\nComplete Apple responsibilities",
            description,
        )
        self.assertIn("Minimum qualifications\nLinux", description)

    @patch("backend.services.job_description_service.requests.get")
    def test_extracts_crossover_job_posting_json_ld(self, mock_get):
        response = Mock()
        response.text = (
            '<script type="application/ld+json">'
            '{"@type":"JobPosting","description":'
            '"<p>Full Crossover role.</p><ul><li>Linux</li></ul>"}'
            "</script>"
        )
        mock_get.return_value = response

        description = JobDescriptionService().enrich(
            "Support Engineer",
            "Trilogy",
            listing_url=(
                "https://www.crossover.com/jobs/123/trilogy/support-engineer"
            ),
        )

        self.assertIn("Full Crossover role.", description)
        self.assertIn("- Linux", description)

    @patch("backend.services.job_description_service.requests.get")
    def test_enriches_amazon_job_with_full_qualification_sections(
        self,
        mock_get,
    ):
        response = Mock()
        response.json.return_value = {
            "jobs": [
                {
                    "title": "Software Development Engineer",
                    "location": "Seattle, USA",
                    "description": "Wrong role",
                },
                {
                    "title": "Datacenter Ops Technician, DCC Communities",
                    "location": "MX, QUE, Queretaro",
                    "description": "<p>Operate AWS infrastructure.</p>",
                    "basic_qualifications": "- Linux<br>- Networking",
                    "preferred_qualifications": "Data center experience",
                },
            ]
        }
        mock_get.return_value = response

        description = JobDescriptionService().enrich(
            title="Datacenter Ops Technician, DCC Communities",
            company="Amazon",
            location="Querétaro",
        )

        self.assertIn("Operate AWS infrastructure.", description)
        self.assertIn("Basic qualifications\n- Linux", description)
        self.assertIn("Preferred qualifications", description)
        self.assertNotIn("<p>", description)

    @patch("backend.services.job_description_service.requests.get")
    def test_uses_greenhouse_api_only_for_recognized_job_urls(
        self,
        mock_get,
    ):
        response = Mock()
        response.json.return_value = {
            "content": "<p>Full role description</p><ul><li>Python</li></ul>"
        }
        mock_get.return_value = response
        service = JobDescriptionService()

        description = service.enrich(
            "Platform Engineer",
            "Example",
            listing_url="https://job-boards.greenhouse.io/example/jobs/12345",
        )

        self.assertIn("Full role description", description)
        self.assertIn("- Python", description)
        called_url = mock_get.call_args.args[0]
        self.assertEqual(
            called_url,
            "https://boards-api.greenhouse.io/v1/boards/example/jobs/12345",
        )

    @patch("backend.services.job_description_service.requests.get")
    def test_uses_lever_posting_api_for_direct_lever_url(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "openingPlain": "Build reliable systems.",
            "lists": [{"text": "Requirements", "content": "Linux<br>Python"}],
        }
        mock_get.return_value = response

        description = JobDescriptionService().enrich(
            "SRE",
            "Example",
            listing_url="https://jobs.lever.co/example/posting-123",
        )

        self.assertIn("Build reliable systems.", description)
        self.assertIn("Requirements\nLinux\nPython", description)

    @patch("backend.services.job_description_service.requests.get")
    def test_uses_ashby_public_board_for_direct_ashby_url(self, mock_get):
        response = Mock()
        response.json.return_value = {
            "jobs": [{
                "jobUrl": "https://jobs.ashbyhq.com/example/posting-123",
                "descriptionPlain": "Complete Ashby description",
            }]
        }
        mock_get.return_value = response

        description = JobDescriptionService().enrich(
            "Engineer",
            "Example",
            listing_url="https://jobs.ashbyhq.com/example/posting-123",
        )

        self.assertEqual(description, "Complete Ashby description")

    @patch("backend.services.job_description_service.requests.get")
    def test_does_not_fetch_arbitrary_listing_urls(self, mock_get):
        description = JobDescriptionService().enrich(
            "Engineer",
            "Example",
            listing_url="http://127.0.0.1/private",
        )

        self.assertIsNone(description)
        mock_get.assert_not_called()

    @patch("backend.services.job_description_service.requests.get")
    def test_rejects_non_https_or_nonstandard_port_listing_urls(
        self,
        mock_get,
    ):
        service = JobDescriptionService()

        for listing_url in (
            "http://jobs.apple.com/en-us/details/123/engineer",
            "https://jobs.apple.com:444/en-us/details/123/engineer",
            "https://user@jobs.apple.com/en-us/details/123/engineer",
        ):
            with self.subTest(listing_url=listing_url):
                self.assertIsNone(
                    service.enrich(
                        "Engineer",
                        "Example",
                        listing_url=listing_url,
                    )
                )

        mock_get.assert_not_called()

    @patch("backend.services.job_description_service.requests.get")
    def test_provider_failure_falls_back_without_breaking_dialog(
        self,
        mock_get,
    ):
        mock_get.side_effect = requests.Timeout("timeout")

        description = JobDescriptionService().enrich(
            "Data Center Technician",
            "Amazon",
            "Queretaro",
        )

        self.assertIsNone(description)


if __name__ == "__main__":
    unittest.main()
