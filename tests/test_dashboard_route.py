import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.routes.dashboard import get_dashboard
from backend.services.dashboard_service import (
    DashboardError,
    ProfileRequiredError,
)


class DashboardRouteTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=21)
        self.service = Mock()

    def test_authenticated_user_is_passed_to_service(self):
        self.service.get_for_user.return_value = {"career_progress": 60}

        result = get_dashboard(self.user, self.service)

        self.assertEqual(result["career_progress"], 60)
        self.service.get_for_user.assert_called_once_with(self.user)

    def test_missing_profile_returns_404(self):
        self.service.get_for_user.side_effect = ProfileRequiredError(
            "Create your profile."
        )

        with self.assertRaises(HTTPException) as context:
            get_dashboard(self.user, self.service)

        self.assertEqual(context.exception.status_code, 404)

    def test_dashboard_failure_returns_502(self):
        self.service.get_for_user.side_effect = DashboardError(
            "Dashboard unavailable."
        )

        with self.assertRaises(HTTPException) as context:
            get_dashboard(self.user, self.service)

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
