import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from backend.dependencies.auth import get_current_admin, is_admin_user


class AdminAuthTests(unittest.TestCase):
    @patch(
        "backend.dependencies.auth.ADMIN_EMAILS",
        {"owner@example.com"},
    )
    def test_configured_admin_email_is_recognized_case_insensitively(self):
        user = SimpleNamespace(
            email="Owner@Example.com",
            is_email_verified=True,
        )

        self.assertTrue(is_admin_user(user))
        self.assertIs(get_current_admin(user), user)

    @patch(
        "backend.dependencies.auth.ADMIN_EMAILS",
        {"owner@example.com"},
    )
    def test_unconfigured_user_is_rejected(self):
        with self.assertRaises(HTTPException) as context:
            get_current_admin(SimpleNamespace(
                email="user@example.com",
                is_email_verified=True,
            ))

        self.assertEqual(context.exception.status_code, 403)

    @patch(
        "backend.dependencies.auth.ADMIN_EMAILS",
        {"owner@example.com"},
    )
    def test_unverified_allowlisted_user_is_rejected(self):
        user = SimpleNamespace(
            email="owner@example.com",
            is_email_verified=False,
        )

        self.assertFalse(is_admin_user(user))
        with self.assertRaises(HTTPException) as context:
            get_current_admin(user)

        self.assertEqual(context.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
