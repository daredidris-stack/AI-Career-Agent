import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.job_search_service import (
    JobSearchError,
    JobSearchService,
    ProfileRequiredError,
)


class JobSearchServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            technical_skills="AWS, Python",
            years_experience=4,
            current_role="Technician",
            target_role="Cloud Engineer",
            professional_summary="Infrastructure operations",
            city="Mexico City",
            country="Mexico",
            preferred_work_mode="Remote",
        )
        self.repository = Mock()
        self.repository.get_by_user_id.return_value = self.profile
        self.resume_repository = Mock()
        self.resume_repository.get_latest_skills_by_user_id.return_value = [
            "Linux",
            "Terraform",
        ]

    def test_authenticated_search_uses_users_database_profile(self):
        aggregator = Mock(
            return_value=[{"title": "Cloud Engineer"}]
        )
        ranker = Mock(
            return_value=[
                {
                    "title": "Cloud Engineer",
                    "analysis": {"match_score": 90},
                }
            ]
        )
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            ranker,
        )

        result = service.search_for_user(
            user_id=42,
            keyword="cloud",
            min_score=80,
        )

        self.repository.get_by_user_id.assert_called_once_with(42)
        aggregator.assert_called_once_with("cloud", "Remote", "")
        candidate_profile = ranker.call_args.args[0]
        self.assertEqual(
            candidate_profile["technical_skills"],
            ["AWS", "Python", "Linux", "Terraform"],
        )
        self.assertEqual(
            ranker.call_args.args[1],
            [{"title": "Cloud Engineer"}],
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["jobs"][0]["analysis"]["match_score"], 90)

    def test_missing_profile_stops_job_search(self):
        self.repository.get_by_user_id.return_value = None
        aggregator = Mock()
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(),
        )

        with self.assertRaises(ProfileRequiredError):
            service.search_for_user(42, "cloud")

        aggregator.assert_not_called()

    def test_provider_failure_returns_service_error(self):
        aggregator = Mock(
            side_effect=RuntimeError("provider unavailable")
        )
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(),
        )

        with self.assertRaises(JobSearchError):
            service.search_for_user(42, "cloud")

    def test_ranking_failure_returns_service_error(self):
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            Mock(return_value=[]),
            Mock(side_effect=RuntimeError("LLM unavailable")),
        )

        with self.assertRaises(JobSearchError):
            service.search_for_user(42, "cloud")

    def test_defaults_search_to_profile_role_and_preferences(self):
        aggregator = Mock(return_value=[])
        ranker = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            ranker,
        )

        result = service.search_for_user(42)

        aggregator.assert_called_once_with(
            "Cloud Engineer",
            "Remote",
            "",
        )
        self.assertEqual(result["filters"]["keyword"], "Cloud Engineer")
        self.assertEqual(result["filters"]["location"], "Remote")

    def test_uses_profile_city_when_remote_is_not_preferred(self):
        self.profile.preferred_work_mode = "Hybrid"
        aggregator = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(return_value=[]),
        )

        service.search_for_user(42)

        aggregator.assert_called_once_with(
            "Cloud Engineer",
            "Mexico City, Mexico",
            "",
        )

    def test_search_filters_override_profile_defaults(self):
        aggregator = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(return_value=[]),
        )

        result = service.search_for_user(
            42,
            keyword="Platform Engineer",
            country="Canada",
            city="Toronto",
            industry="Finance",
            work_mode="Hybrid",
        )

        aggregator.assert_called_once_with(
            "Platform Engineer",
            "Toronto, Canada",
            "Finance",
        )
        self.assertEqual(result["filters"]["industry"], "Finance")


if __name__ == "__main__":
    unittest.main()
