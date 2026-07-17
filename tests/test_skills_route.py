import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.routes.skills import analyze_skills
from backend.services.skill_gap_service import (
    ProfileRequiredError,
    SkillGapError,
)


class SkillsRouteTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=11)
        self.service = Mock()

    def test_authenticated_user_is_passed_to_service(self):
        self.service.analyze_for_user.return_value = {
            "current_skills": ["AWS"],
            "missing_skills": ["Terraform"],
            "recommendation": "Learn Terraform.",
        }

        result = analyze_skills(
            self.user,
            self.service,
        )

        self.assertEqual(result["current_skills"], ["AWS"])
        self.service.analyze_for_user.assert_called_once_with(11)

    def test_missing_profile_returns_404(self):
        self.service.analyze_for_user.side_effect = (
            ProfileRequiredError("Create your profile.")
        )

        with self.assertRaises(HTTPException) as context:
            analyze_skills(self.user, self.service)

        self.assertEqual(context.exception.status_code, 404)

    def test_analysis_failure_returns_502(self):
        self.service.analyze_for_user.side_effect = (
            SkillGapError("Analysis unavailable")
        )

        with self.assertRaises(HTTPException) as context:
            analyze_skills(self.user, self.service)

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
