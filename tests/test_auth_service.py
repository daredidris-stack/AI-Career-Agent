import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    LoginLockedError,
)
from backend.services.auth_service import AuthService, MAX_FAILED_LOGINS


class AuthServiceTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(
            id=7,
            email="user@example.com",
            password_hash="hash",
            token_version=0,
            failed_login_attempts=0,
            locked_until=None,
            is_email_verified=False,
        )
        self.repository = Mock()
        self.repository.get_by_email.return_value = self.user
        self.service = AuthService(self.repository)

    @patch("backend.services.auth_service.verify_password", return_value=False)
    def test_repeated_failed_logins_lock_account(self, _verify):
        for _ in range(MAX_FAILED_LOGINS - 1):
            with self.assertRaises(InvalidCredentialsError):
                self.service.authenticate_user(self.user.email, "wrong")

        with self.assertRaises(LoginLockedError):
            self.service.authenticate_user(self.user.email, "wrong")

        self.assertIsNotNone(self.user.locked_until)
        self.assertEqual(self.repository.save.call_count, MAX_FAILED_LOGINS)

    @patch("backend.services.auth_service.create_access_token", return_value="token")
    @patch("backend.services.auth_service.verify_password", return_value=True)
    def test_successful_login_resets_failures_and_versions_token(
        self,
        _verify,
        create_token,
    ):
        self.user.failed_login_attempts = 2

        token = self.service.authenticate_user(self.user.email, "correct")

        self.assertEqual(token, "token")
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.repository.save.assert_called_once_with(self.user)
        self.assertEqual(
            create_token.call_args.args[0]["token_version"],
            0,
        )

    @patch("backend.services.auth_service.verify_password", return_value=True)
    def test_account_deletion_requires_password_and_deletes_user(self, _verify):
        self.service.delete_account(self.user, "correct")

        self.repository.delete_user.assert_called_once_with(self.user)

    @patch("backend.services.auth_service.verify_password", return_value=False)
    def test_account_deletion_rejects_wrong_password(self, _verify):
        with self.assertRaises(InvalidCredentialsError):
            self.service.delete_account(self.user, "wrong")

        self.repository.delete_user.assert_not_called()

    @patch("backend.services.auth_service.create_action_token", return_value="verify-token")
    def test_verification_email_contains_frontend_link(self, _create_token):
        email_service = Mock()
        service = AuthService(self.repository, email_service)

        service.send_verification(self.user.email)

        body = email_service.send.call_args.args[2]
        self.assertIn("/verify-email?token=verify-token", body)

    @patch("backend.services.auth_service.create_action_token", return_value="reset-token")
    def test_password_reset_request_does_not_disclose_missing_account(self, _create_token):
        self.repository.get_by_email.return_value = None
        email_service = Mock()
        service = AuthService(self.repository, email_service)

        service.send_password_reset("missing@example.com")

        email_service.send.assert_not_called()

    @patch("backend.services.auth_service.hash_password", return_value="new-hash")
    @patch(
        "backend.services.auth_service.decode_action_token",
        return_value={"user_id": 7, "token_version": 0},
    )
    def test_password_reset_changes_password_and_revokes_tokens(
        self,
        _decode,
        _hash,
    ):
        self.repository.get_by_id.return_value = self.user

        self.service.reset_password("token", "new-password")

        self.assertEqual(self.user.password_hash, "new-hash")
        self.assertEqual(self.user.token_version, 1)
        self.repository.save.assert_called_with(self.user)

    @patch(
        "backend.services.auth_service.decode_action_token",
        return_value={"user_id": 7, "token_version": 0},
    )
    def test_email_confirmation_marks_account_verified(self, _decode):
        self.repository.get_by_id.return_value = self.user

        self.service.confirm_verification("token")

        self.assertTrue(self.user.is_email_verified)
        self.repository.save.assert_called_with(self.user)


if __name__ == "__main__":
    unittest.main()
