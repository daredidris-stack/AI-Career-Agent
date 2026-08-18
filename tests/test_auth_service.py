import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.exceptions.auth_exceptions import (
    InvalidCredentialsError,
    LoginLockedError,
    GoogleAccountConflictError,
)
from backend.services.auth_service import AuthService, MAX_FAILED_LOGINS
from backend.services.google_identity_service import GoogleIdentity
from backend.repositories.refresh_token_repository import RefreshTokenRepository
from backend.core.time import utc_now
from datetime import timedelta
import hashlib
import secrets


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
            google_subject=None,
            first_name=None,
            last_name=None,
            terms_accepted_at=None,
            terms_version=None,
        )
        self.repository = Mock()
        self.repository.get_by_email.return_value = self.user
        self.refresh_token_repo = Mock(spec=RefreshTokenRepository)
        self.service = AuthService(self.repository, None, self.refresh_token_repo)

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

        access_token, refresh_token = self.service.authenticate_user(self.user.email, "correct")

        self.assertEqual(access_token, "token")
        self.assertEqual(self.user.failed_login_attempts, 0)
        self.repository.save.assert_called_once_with(self.user)
        self.assertEqual(
            create_token.call_args.args[0]["token_version"],
            0,
        )
        # Ensure a refresh token was created
        self.refresh_token_repo.create.assert_called_once()
        args, kwargs = self.refresh_token_repo.create.call_args
        self.assertEqual(kwargs["user_id"], self.user.id)
        self.assertIsInstance(kwargs["token_hash"], str)
        self.assertGreater(kwargs["expires_at"], utc_now())

    @patch("backend.services.auth_service.verify_password", return_value=True)
    def test_account_deletion_requires_password_and_deletes_user(self, _verify):
        self.service.delete_account(self.user, "correct")

        self.repository.delete_user.assert_called_once_with(self.user)

    @patch("backend.services.auth_service.verify_password", return_value=False)
    def test_account_deletion_rejects_wrong_password(self, _verify):
        with self.assertRaises(InvalidCredentialsError):
            self.service.delete_account(self.user, "wrong")

        self.repository.delete_user.assert_not_called()

    @patch("backend.services.auth_service.hash_password", return_value="hash")
    def test_registration_records_versioned_terms_acceptance(self, _hash):
        self.repository.get_by_email.return_value = None
        self.repository.create_user.return_value = self.user

        self.service.register_user("user@example.com", "password")

        values = self.repository.create_user.call_args.kwargs
        self.assertIsNotNone(values["terms_accepted_at"])
        self.assertTrue(values["terms_version"])

    @patch("backend.services.auth_service.create_action_token", return_value="verify-token")
    def test_verification_email_contains_frontend_link(self, _create_token):
        email_service = Mock()
        service = AuthService(self.repository, email_service, None)

        service.send_verification(self.user.email)

        body = email_service.send.call_args.args[2]
        self.assertIn("/verify-email?token=verify-token", body)

    @patch("backend.services.auth_service.create_action_token", return_value="reset-token")
    def test_password_reset_request_does_not_disclose_missing_account(self, _create_token):
        self.repository.get_by_email.return_value = None
        email_service = Mock()
        service = AuthService(self.repository, email_service, None)

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

    @patch("backend.services.auth_service.create_access_token", return_value="token")
    @patch("backend.services.auth_service.hash_password", return_value="hash")
    def test_google_login_creates_verified_account_with_terms(
        self,
        _hash,
        _create_token,
    ):
        self.repository.get_by_google_subject.return_value = None
        self.repository.get_by_email.return_value = None
        self.repository.create_user.return_value = self.user
        identity = GoogleIdentity(
            subject="google-user-123",
            email="user@gmail.com",
            first_name="Dare",
            last_name="Daniel",
        )

        access_token, refresh_token = self.service.authenticate_google(identity)

        self.assertEqual(access_token, "token")
        values = self.repository.create_user.call_args.kwargs
        self.assertEqual(values["google_subject"], "google-user-123")
        self.assertTrue(values["is_email_verified"])
        self.assertEqual(values["first_name"], "Dare")
        self.assertIsNotNone(values["terms_accepted_at"])
        self.assertTrue(values["terms_version"])

    @patch("backend.services.auth_service.create_access_token", return_value="token")
    def test_google_login_links_existing_verified_email(
        self,
        _create_token,
    ):
        self.repository.get_by_google_subject.return_value = None
        self.repository.get_by_email.return_value = self.user
        identity = GoogleIdentity(
            subject="google-user-123",
            email=self.user.email,
            first_name="Dare",
            hosted_domain="example.com",
        )

        access_token, refresh_token = self.service.authenticate_google(identity)

        self.assertEqual(access_token, "token")
        self.assertEqual(self.user.google_subject, "google-user-123")
        self.assertTrue(self.user.is_email_verified)
        self.assertEqual(self.user.first_name, "Dare")
        self.assertIsNotNone(self.user.terms_accepted_at)
        self.assertTrue(self.user.terms_version)
        self.repository.save.assert_called_with(self.user)

    @patch("backend.services.auth_service.create_access_token", return_value="token")
    def test_google_login_records_terms_for_already_linked_account(
        self,
        _create_token,
    ):
        self.user.google_subject = "google-user-123"
        self.repository.get_by_google_subject.return_value = self.user

        access_token, refresh_token = self.service.authenticate_google(GoogleIdentity(
            subject="google-user-123",
            email=self.user.email,
        ))

        self.assertEqual(access_token, "token")
        self.assertIsNotNone(self.user.terms_accepted_at)
        self.assertTrue(self.user.terms_version)
        self.repository.save.assert_called_with(self.user)

    def test_google_login_rejects_conflicting_link(self):
        self.repository.get_by_google_subject.return_value = None
        self.repository.get_by_email.return_value = self.user
        self.user.google_subject = "different-google-user"

        with self.assertRaises(GoogleAccountConflictError):
            self.service.authenticate_google(GoogleIdentity(
                subject="google-user-123",
                email=self.user.email,
                hosted_domain="example.com",
            ))

    def test_google_login_rejects_non_authoritative_email_link(self):
        self.repository.get_by_google_subject.return_value = None

        with self.assertRaises(GoogleAccountConflictError):
            self.service.authenticate_google(GoogleIdentity(
                subject="google-user-123",
                email="user@example.com",
            ))

        self.repository.get_by_email.assert_not_called()

    # Refresh token tests
    def test_create_refresh_token_for_user(self):
        # Arrange
        fixed_expires = utc_now() + timedelta(days=30)
        self.refresh_token_repo.create.return_value = SimpleNamespace(
            id=1,
            user_id=self.user.id,
            token_hash="dummy",
            expires_at=fixed_expires,
            revoked_at=None,
            created_at=utc_now(),
        )

        # Act
        result = self.service._create_refresh_token_for_user(self.user)

        # Assert
        self.assertIsInstance(result, str)
        self.refresh_token_repo.create.assert_called_once()
        args, kwargs = self.refresh_token_repo.create.call_args
        self.assertEqual(kwargs["user_id"], self.user.id)
        # Check that the expires_at is approximately equal to fixed_expires (within 1 second)
        self.assertAlmostEqual(kwargs["expires_at"], fixed_expires, delta=timedelta(seconds=1))
        # The token hash should be the SHA-256 of the returned token
        expected_hash = hashlib.sha256(result.encode()).hexdigest()
        self.assertEqual(kwargs["token_hash"], expected_hash)

    def test_get_user_id_from_refresh_token_valid(self):
        # Arrange
        plain_token = "valid-token"
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        stored = SimpleNamespace(
            id=1,
            user_id=self.user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(days=1),
            revoked_at=None,
        )
        self.refresh_token_repo.get_by_token_hash.return_value = stored

        # Act
        user_id = self.service._get_user_id_from_refresh_token(plain_token)

        # Assert
        self.assertEqual(user_id, self.user.id)
        self.refresh_token_repo.get_by_token_hash.assert_called_once_with(token_hash)

    def test_get_user_id_from_refresh_token_invalid_hash(self):
        # Arrange
        self.refresh_token_repo.get_by_token_hash.return_value = None

        # Act
        user_id = self.service._get_user_id_from_refresh_token("invalid-token")

        # Assert
        self.assertIsNone(user_id)

    def test_get_user_id_from_refresh_token_revoked(self):
        # Arrange
        plain_token = "revoked-token"
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        stored = SimpleNamespace(
            id=1,
            user_id=self.user.id,
            token_hash=token_hash,
            expires_at=utc_now() + timedelta(days=1),
            revoked_at=utc_now(),  # revoked now
        )
        self.refresh_token_repo.get_by_token_hash.return_value = stored

        # Act
        user_id = self.service._get_user_id_from_refresh_token(plain_token)

        # Assert
        self.assertIsNone(user_id)

    def test_get_user_id_from_refresh_token_expired(self):
        # Arrange
        plain_token = "expired-token"
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        stored = SimpleNamespace(
            id=1,
            user_id=self.user.id,
            token_hash=token_hash,
            expires_at=utc_now() - timedelta(days=1),  # expired yesterday
            revoked_at=None,
        )
        self.refresh_token_repo.get_by_token_hash.return_value = stored

        # Act
        user_id = self.service._get_user_id_from_refresh_token(plain_token)

        # Assert
        self.assertIsNone(user_id)

    def test_rotate_refresh_token_success(self):
        # Arrange
        old_token = "old-refresh-token"
        old_token_hash = hashlib.sha256(old_token.encode()).hexdigest()
        new_token = "new-refresh-token"
        new_token_hash = hashlib.sha256(new_token.encode()).hexdigest()

        # Mock the validation of the old token
        with patch.object(self.service, '_get_user_id_from_refresh_token', return_value=self.user.id):
            # Mock the revoke of the old token
            self.refresh_token_repo.revoke.return_value = None
            # Mock the creation of the new refresh token
            self.service._create_refresh_token_for_user = Mock(return_value=new_token)
            # Mock the repository.get_by_id to return a user with id, email, and token_version
            self.repository.get_by_id.return_value = SimpleNamespace(
                id=self.user.id,
                email=self.user.email,
                token_version=self.user.token_version,
            )

            # Act
            access_token, refresh_token = self.service.rotate_refresh_token(old_token)

            # Assert
            self.assertIsNotNone(access_token)
            self.assertIsNotNone(refresh_token)
            self.assertEqual(refresh_token, new_token)
            # Ensure the old token was revoked
            self.refresh_token_repo.revoke.assert_called_once_with(old_token_hash)
            # Ensure a new refresh token was created
            self.service._create_refresh_token_for_user.assert_called_once()
            # Check that the user passed to _create_refresh_token_for_user has the expected id
            args, kwargs = self.service._create_refresh_token_for_user.call_args
            self.assertEqual(args[0].id, self.user.id)
            self.assertEqual(args[0].email, self.user.email)
            self.assertEqual(args[0].token_version, self.user.token_version)

    def test_rotate_refresh_token_invalid_token(self):
        # Arrange
        with patch.object(self.service, '_get_user_id_from_refresh_token', return_value=None):
            # Act
            access_token, refresh_token = self.service.rotate_refresh_token("invalid-token")

            # Assert
            self.assertIsNone(access_token)
            self.assertIsNone(refresh_token)
            self.refresh_token_repo.revoke.assert_not_called()

    def test_rotate_refresh_token_user_not_found(self):
        # Arrange
        with patch.object(self.service, '_get_user_id_from_refresh_token', return_value=self.user.id):
            self.repository.get_by_id.return_value = None
            # Act
            access_token, refresh_token = self.service.rotate_refresh_token("some-token")

            # Assert
            self.assertIsNone(access_token)
            self.assertIsNone(refresh_token)

    def test_revoke_refresh_token(self):
        # Arrange
        token = "token-to-revoke"
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        # Act
        self.service.revoke_refresh_token(token)
        # Assert
        self.refresh_token_repo.revoke.assert_called_once_with(token_hash)

    def test_revoke_all_refresh_tokens_for_user(self):
        # Arrange
        user_id = self.user.id
        # Act
        self.service.revoke_all_refresh_tokens_for_user(user_id)
        # Assert
        self.refresh_token_repo.revoke_all_for_user.assert_called_once_with(user_id)


if __name__ == "__main__":
    unittest.main()
