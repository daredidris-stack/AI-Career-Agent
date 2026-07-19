import unittest
from unittest.mock import Mock, patch

from job_search import search_jobs


class RemoteOkApiTests(unittest.TestCase):
    @patch("job_search.requests.get")
    def test_matches_common_site_reliability_title_variants(self, mock_get):
        response = Mock()
        response.json.return_value = [
            {"legal": "metadata"},
            {
                "position": "Senior SRE",
                "company": "Example Cloud",
                "url": "https://remoteok.com/remote-jobs/1",
            },
            {
                "position": "Platform Engineer",
                "company": "Example Platform",
                "url": "https://remoteok.com/remote-jobs/2",
            },
            {
                "position": "DevOps Engineer",
                "company": "Example Operations",
                "url": "https://remoteok.com/remote-jobs/4",
            },
            {
                "position": "Product Designer",
                "company": "Example Design",
                "url": "https://remoteok.com/remote-jobs/3",
            },
        ]
        mock_get.return_value = response

        jobs = search_jobs("Site Reliability Engineer")

        self.assertEqual(
            [job["title"] for job in jobs],
            ["Senior SRE", "Platform Engineer", "DevOps Engineer"],
        )
        response.raise_for_status.assert_called_once()


if __name__ == "__main__":
    unittest.main()
