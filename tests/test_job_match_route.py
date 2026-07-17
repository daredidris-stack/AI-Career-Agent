import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.routes.job_match import (
    JobMatchRequest,
    match_job,
)
from backend.services.job_match_service import (
    JobMatchError,
    ProfileRequiredError,
)


class JobMatchRouteTests(unittest.TestCase):
    def setUp(self):
        self.request = JobMatchRequest(
            job_description="Cloud role",
        )
        self.user = SimpleNamespace(id=10)
        self.service = Mock()

    def test_authenticated_user_is_passed_to_service(self):
        self.service.match_for_user.return_value = {
            "match_score": 80,
            "matching_skills": [],
            "missing_skills": [],
            "recommendation": "",
        }

        result = match_job(
            self.request,
            self.user,
            self.service,
        )

        self.assertEqual(result["match_score"], 80)
        self.service.match_for_user.assert_called_once_with(
            user_id=10,
            resume=None,
            job_description="Cloud role",
        )

    def test_missing_profile_returns_404(self):
        self.service.match_for_user.side_effect = (
            ProfileRequiredError("Create your profile.")
        )

        with self.assertRaises(HTTPException) as context:
            match_job(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 404)

    def test_invalid_input_returns_400(self):
        self.service.match_for_user.side_effect = ValueError(
            "Resume cannot be empty."
        )

        with self.assertRaises(HTTPException) as context:
            match_job(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_ai_failure_returns_502(self):
        self.service.match_for_user.side_effect = (
            JobMatchError("AI unavailable")
        )

        with self.assertRaises(HTTPException) as context:
            match_job(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
