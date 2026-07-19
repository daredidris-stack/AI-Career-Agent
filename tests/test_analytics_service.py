import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.analytics_service import (
    AnalyticsError,
    AnalyticsService,
    ProfileRequiredError,
)


class AnalyticsServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            phone="555-0100",
            country="Mexico",
            state=None,
            city="Mexico City",
            current_role="Developer",
            target_role="Cloud Engineer",
            years_experience=3,
            professional_summary=None,
            technical_skills="Python, AWS",
            soft_skills=None,
            linkedin=None,
            github=None,
            portfolio=None,
            preferred_job_type="Full-time",
            preferred_work_mode="Remote",
        )
        self.profile_repository = Mock()
        self.profile_repository.get_by_user_id.return_value = self.profile
        self.job_catalog_repository = Mock()
        self.job_catalog_repository.list_jobs.return_value = [
            {"title": "Cloud Engineer"},
            {"title": "Platform Engineer"},
        ]
        self.resume_analysis_repository = Mock()
        self.resume_analysis_repository.get_latest_skills_by_user_id.return_value = [
            "Terraform",
        ]
        self.analyzer = Mock(
            return_value={
                "current_skills": ["Python", "AWS"],
                "missing_skills": ["Terraform"],
            }
        )
        self.service = AnalyticsService(
            self.profile_repository,
            self.job_catalog_repository,
            self.resume_analysis_repository,
            self.analyzer,
        )

    def test_builds_profile_driven_analytics(self):
        result = self.service.get_for_user(7)

        self.profile_repository.get_by_user_id.assert_called_once_with(7)
        analyzer_profile = self.analyzer.call_args.args[0]
        self.assertEqual(
            analyzer_profile["technical_skills"],
            ["Python", "AWS", "Terraform"],
        )
        self.assertEqual(
            self.analyzer.call_args.args[1],
            self.job_catalog_repository.list_jobs.return_value,
        )
        self.assertEqual(result["profile_completion"], 60)
        self.assertEqual(result["skills_completed"], 2)
        self.assertEqual(result["skill_gap"], 1)
        self.assertEqual(result["jobs_available"], 2)
        self.assertEqual(result["weekly_progress"], [])

    def test_missing_profile_stops_analytics(self):
        self.profile_repository.get_by_user_id.return_value = None

        with self.assertRaises(ProfileRequiredError):
            self.service.get_for_user(7)

        self.job_catalog_repository.list_jobs.assert_not_called()

    def test_unpersonalized_dashboard_activity_does_not_require_profile(self):
        self.profile_repository.get_by_user_id.return_value = None

        result = self.service.get_unpersonalized(7)

        self.assertEqual(result["jobs_available"], 2)
        self.assertEqual(result["document_counts"], {})
        self.assertEqual(result["application_pipeline"], {})
        self.assertEqual(result["ai_requests_30d"], 0)
        self.profile_repository.get_by_user_id.assert_not_called()

    def test_catalog_failure_returns_service_error(self):
        self.job_catalog_repository.list_jobs.side_effect = ValueError(
            "Invalid catalog"
        )

        with self.assertRaises(AnalyticsError):
            self.service.get_for_user(7)

    def test_analysis_failure_returns_service_error(self):
        self.analyzer.side_effect = RuntimeError("AI unavailable")

        with self.assertRaises(AnalyticsError):
            self.service.get_for_user(7)


if __name__ == "__main__":
    unittest.main()
