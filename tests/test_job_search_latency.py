import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.job_search_service import JobSearchService


class JobSearchLatencyTests(unittest.TestCase):
    def test_search_can_rank_without_waiting_for_ai(self):
        profile = SimpleNamespace(
            technical_skills="AWS, Linux",
            target_role="Site Reliability Engineer",
            current_role="Technician",
            country="Worldwide",
            city="",
            preferred_work_mode="Remote",
        )
        profiles = Mock()
        profiles.get_by_user_id.return_value = profile
        analyses = Mock()
        analyses.get_latest_skills_by_user_id.return_value = []
        ai_ranker = Mock(side_effect=RuntimeError("must not be called"))
        service = JobSearchService(
            profiles,
            analyses,
            Mock(return_value=[{
                "title": "Site Reliability Engineer",
                "description": "AWS and Linux operations",
            }]),
            ai_ranker,
            enable_ai_ranking=False,
        )

        result = service.search_for_user(7)

        ai_ranker.assert_not_called()
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["jobs"][0]["analysis"]["match_score"], 100)


if __name__ == "__main__":
    unittest.main()
