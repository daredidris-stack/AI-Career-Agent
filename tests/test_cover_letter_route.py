import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.routes.cover_letter import (
    CoverLetterRequest,
    generate_cover_letter,
)
from backend.services.cover_letter_service import (
    CoverLetterError,
    ProfileRequiredError,
)


class CoverLetterRouteTests(unittest.TestCase):
    def setUp(self):
        self.request = CoverLetterRequest(
            job_description="Cloud role",
        )
        self.user = SimpleNamespace(id=9)
        self.service = Mock()

    def test_authenticated_user_is_passed_to_service(self):
        self.service.generate_for_user.return_value = {
            "cover_letter": "Letter"
        }

        result = generate_cover_letter(
            self.request,
            self.user,
            self.service,
        )

        self.assertEqual(result, {"cover_letter": "Letter"})
        self.service.generate_for_user.assert_called_once_with(
            user_id=9,
            resume=None,
            job_description="Cloud role",
        )

    def test_missing_profile_returns_404(self):
        self.service.generate_for_user.side_effect = (
            ProfileRequiredError("Create your profile.")
        )

        with self.assertRaises(HTTPException) as context:
            generate_cover_letter(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 404)

    def test_invalid_input_returns_400(self):
        self.service.generate_for_user.side_effect = ValueError(
            "Resume cannot be empty."
        )

        with self.assertRaises(HTTPException) as context:
            generate_cover_letter(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_ai_failure_returns_502(self):
        self.service.generate_for_user.side_effect = (
            CoverLetterError("AI unavailable")
        )

        with self.assertRaises(HTTPException) as context:
            generate_cover_letter(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
