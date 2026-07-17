import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.routes.analytics import get_analytics
from backend.services.analytics_service import (
    AnalyticsError,
    ProfileRequiredError,
)


class AnalyticsRouteTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=13)
        self.service = Mock()

    def test_authenticated_user_is_passed_to_service(self):
        self.service.get_for_user.return_value = {
            "profile_completion": 60,
            "skills_completed": 2,
            "skill_gap": 1,
            "jobs_available": 2,
            "current_skills": ["Python", "AWS"],
            "missing_skills": ["Terraform"],
            "weekly_progress": [],
        }

        result = get_analytics(self.user, self.service)

        self.assertEqual(result["profile_completion"], 60)
        self.service.get_for_user.assert_called_once_with(13)

    def test_missing_profile_returns_404(self):
        self.service.get_for_user.side_effect = ProfileRequiredError(
            "Create your profile."
        )

        with self.assertRaises(HTTPException) as context:
            get_analytics(self.user, self.service)

        self.assertEqual(context.exception.status_code, 404)

    def test_analytics_failure_returns_502(self):
        self.service.get_for_user.side_effect = AnalyticsError(
            "Analytics unavailable."
        )

        with self.assertRaises(HTTPException) as context:
            get_analytics(self.user, self.service)

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
