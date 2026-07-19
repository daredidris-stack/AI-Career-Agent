import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.analytics_service import AnalyticsError
from backend.services.dashboard_service import (
    DashboardError,
    DashboardService,
    ProfileRequiredError,
)


class DashboardServiceTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id=9,
            email="ada@example.com",
            first_name="Ada",
            last_name="Lovelace",
        )
        self.profile = SimpleNamespace(
            current_role="Developer",
            target_role="Cloud Engineer",
            city="Mexico City",
            country="Mexico",
            preferred_job_type="Full-time",
            preferred_work_mode="Remote",
        )
        self.profile_repository = Mock()
        self.profile_repository.get_by_user_id.return_value = self.profile
        self.analytics_service = Mock()
        self.analytics_service.get_unpersonalized.return_value = {
            "jobs_available": 3,
            "weekly_progress": [],
            "document_counts": {},
            "application_pipeline": {},
            "ai_requests_30d": 0,
        }
        self.analytics_service.get_for_profile.return_value = {
            "profile_completion": 60,
            "skills_completed": 2,
            "skill_gap": 1,
            "jobs_available": 3,
            "current_skills": ["Python", "AWS"],
            "missing_skills": ["Terraform"],
            "weekly_progress": [],
        }
        self.resume_analysis_repository = Mock()
        self.resume_analysis_repository.get_latest_by_user_id.return_value = (
            SimpleNamespace(resume_score=84, ats_score=79)
        )
        self.service = DashboardService(
            self.profile_repository,
            self.analytics_service,
            self.resume_analysis_repository,
        )

    def test_builds_dashboard_from_profile_and_analytics(self):
        result = self.service.get_for_user(self.user)

        self.profile_repository.get_by_user_id.assert_called_once_with(9)
        self.analytics_service.get_for_profile.assert_called_once_with(
            self.profile,
            9,
        )
        self.assertEqual(result["user"]["name"], "Ada Lovelace")
        self.assertEqual(result["jobs_available"], 3)
        self.assertEqual(result["recommended_skill"]["name"], "Terraform")
        self.assertEqual(result["resume_score"], 84)
        self.assertEqual(result["ats_score"], 79)
        self.assertEqual(result["recent_activity"], [])

    def test_missing_profile_returns_onboarding_dashboard(self):
        self.profile_repository.get_by_user_id.return_value = None

        result = self.service.get_for_user(self.user)

        self.assertTrue(result["profile_missing"])
        self.assertEqual(result["career_progress"], 0)
        self.assertEqual(result["profile"]["target_role"], "")
        self.assertEqual(result["jobs_available"], 3)
        self.analytics_service.get_unpersonalized.assert_called_once_with(9)
        self.analytics_service.get_for_profile.assert_not_called()
        self.resume_analysis_repository.get_latest_by_user_id.assert_not_called()

    def test_dashboard_supports_user_without_resume_analysis(self):
        self.resume_analysis_repository.get_latest_by_user_id.return_value = (
            None
        )

        result = self.service.get_for_user(self.user)

        self.assertIsNone(result["resume_score"])
        self.assertIsNone(result["ats_score"])

    def test_analytics_failure_returns_dashboard_error(self):
        self.analytics_service.get_for_profile.side_effect = AnalyticsError(
            "Unavailable"
        )

        with self.assertRaises(DashboardError):
            self.service.get_for_user(self.user)


if __name__ == "__main__":
    unittest.main()
