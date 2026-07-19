import unittest
from unittest.mock import Mock, patch

from arbeitnow_api import search_jobs


JOBS = [
    {
        "title": "Site Reliability Engineer",
        "company_name": "Example Cloud",
        "location": "Berlin, Germany",
        "remote": True,
        "description": "<p>Cloud infrastructure and Kubernetes</p>",
        "tags": ["DevOps", "Kubernetes"],
        "url": "https://example.com/sre",
    },
    {
        "title": "Finance Platform Engineer",
        "company_name": "Example Bank",
        "location": "Toronto, Canada",
        "remote": False,
        "description": "Financial technology platform",
        "tags": ["Finance"],
        "url": "https://example.com/platform",
    },
]


class ArbeitnowApiTests(unittest.TestCase):
    def setUp(self):
        self.response = Mock()
        self.response.json.return_value = {"data": JOBS}

    @patch("arbeitnow_api.requests.get")
    def test_sre_alias_matches_site_reliability_role(self, mock_get):
        mock_get.return_value = self.response

        jobs = search_jobs("SRE", "Worldwide")

        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]["title"], "Site Reliability Engineer")
        self.assertNotIn("<p>", jobs[0]["description"])
        self.response.raise_for_status.assert_called_once()

    @patch("arbeitnow_api.requests.get")
    def test_filters_by_location_and_industry(self, mock_get):
        mock_get.return_value = self.response

        jobs = search_jobs(
            "Platform Engineer",
            "Toronto, Canada",
            "Finance",
        )

        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["company"], "Example Bank")

    @patch("arbeitnow_api.requests.get")
    def test_remote_filter_excludes_onsite_roles(self, mock_get):
        mock_get.return_value = self.response

        jobs = search_jobs("Engineer", "Remote")

        self.assertEqual(len(jobs), 1)
        self.assertTrue(jobs[0]["title"].startswith("Site Reliability"))

    @patch("arbeitnow_api.requests.get")
    def test_full_sre_role_uses_related_title_aliases(self, mock_get):
        mock_get.return_value = self.response

        jobs = search_jobs("Site Reliability Engineer", "Worldwide")

        self.assertEqual(len(jobs), 2)


if __name__ == "__main__":
    unittest.main()
