import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.skill_gap_service import (
    ProfileRequiredError,
    SkillGapError,
    SkillGapService,
)


class SkillGapServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            technical_skills="AWS, Linux",
            target_role="Cloud Engineer",
        )
        self.profile_repository = Mock()
        self.profile_repository.get_by_user_id.return_value = (
            self.profile
        )
        self.job_catalog_repository = Mock()
        self.job_catalog_repository.list_jobs.return_value = [
            {
                "title": "Cloud Engineer",
                "skills": ["AWS", "Terraform"],
            }
        ]
        self.resume_analysis_repository = Mock()
        self.resume_analysis_repository.get_latest_skills_by_user_id.return_value = [
            "Python",
            "AWS",
        ]
        self.analyzer = Mock(
            return_value={
                "current_skills": ["AWS", "Linux"],
                "missing_skills": ["Terraform"],
                "recommendation": "Learn Terraform.",
            }
        )
        self.service = SkillGapService(
            self.profile_repository,
            self.job_catalog_repository,
            self.resume_analysis_repository,
            self.analyzer,
        )

    def test_analyzes_database_profile_against_job_catalog(self):
        result = self.service.analyze_for_user(4)

        self.profile_repository.get_by_user_id.assert_called_once_with(4)
        analyzer_profile = self.analyzer.call_args.args[0]
        self.assertEqual(
            analyzer_profile["technical_skills"],
            ["AWS", "Linux", "Python"],
        )
        self.assertEqual(
            self.analyzer.call_args.args[1],
            self.job_catalog_repository.list_jobs.return_value,
        )
        self.assertEqual(
            result["missing_skills"],
            ["Terraform"],
        )

    def test_missing_profile_stops_analysis(self):
        self.profile_repository.get_by_user_id.return_value = None

        with self.assertRaises(ProfileRequiredError):
            self.service.analyze_for_user(4)

        self.job_catalog_repository.list_jobs.assert_not_called()
        self.resume_analysis_repository.get_latest_skills_by_user_id.assert_not_called()

    def test_catalog_failure_returns_service_error(self):
        self.job_catalog_repository.list_jobs.side_effect = (
            ValueError("Invalid catalog")
        )

        with self.assertRaises(SkillGapError):
            self.service.analyze_for_user(4)

    def test_analyzer_failure_returns_service_error(self):
        self.analyzer.side_effect = RuntimeError(
            "Ollama unavailable"
        )

        with self.assertRaises(SkillGapError):
            self.service.analyze_for_user(4)


if __name__ == "__main__":
    unittest.main()
