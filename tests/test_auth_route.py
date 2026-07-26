import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.models.schemas import GoogleLoginRequest, LoginRequest
from backend.routes.auth import google_login, login, swagger_login
from backend.services.google_identity_service import (
    GoogleIdentity,
    GoogleIdentityError,
    GoogleIdentityNotConfiguredError,
)
from backend.services.turnstile_service import (
    TurnstileUnavailableError,
    TurnstileVerificationError,
)


class AuthRouteTests(unittest.TestCase):
    def setUp(self):
        self.auth_service = Mock()
        self.auth_service.authenticate_user.return_value = "access-token"
        self.turnstile = Mock()

    def test_json_login_validates_turnstile_before_authentication(self):
        result = login(
            LoginRequest(
                email="user@example.com",
                password="password",
                turnstile_token="challenge-token",
            ),
            self.auth_service,
            self.turnstile,
        )

        self.turnstile.verify.assert_called_once_with(
            "challenge-token",
            expected_action="login",
        )
        self.auth_service.authenticate_user.assert_called_once_with(
            "user@example.com",
            "password",
        )
        self.assertEqual(result.access_token, "access-token")

    def test_invalid_challenge_stops_authentication(self):
        self.turnstile.verify.side_effect = TurnstileVerificationError()

        with self.assertRaises(HTTPException) as context:
            login(
                LoginRequest(
                    email="user@example.com",
                    password="password",
                    turnstile_token="invalid-token",
                ),
                self.auth_service,
                self.turnstile,
            )

        self.assertEqual(context.exception.status_code, 400)
        self.auth_service.authenticate_user.assert_not_called()

    def test_provider_outage_returns_service_unavailable(self):
        self.turnstile.verify.side_effect = TurnstileUnavailableError()

        with self.assertRaises(HTTPException) as context:
            login(
                LoginRequest(
                    email="user@example.com",
                    password="password",
                    turnstile_token="challenge-token",
                ),
                self.auth_service,
                self.turnstile,
            )

        self.assertEqual(context.exception.status_code, 503)
        self.auth_service.authenticate_user.assert_not_called()

    def test_oauth_token_endpoint_requires_turnstile_too(self):
        result = swagger_login(
            SimpleNamespace(
                username="user@example.com",
                password="password",
            ),
            self.auth_service,
            self.turnstile,
            "challenge-token",
        )

        self.turnstile.verify.assert_called_once_with(
            "challenge-token",
            expected_action="login",
        )
        self.assertEqual(result.access_token, "access-token")

    def test_google_login_verifies_credential_and_returns_app_token(self):
        google_identity = Mock()
        identity = GoogleIdentity(
            subject="google-user-123",
            email="user@gmail.com",
        )
        google_identity.verify.return_value = identity
        self.auth_service.authenticate_google.return_value = "google-token"

        result = google_login(
            GoogleLoginRequest(
                credential="x" * 100,
                accept_terms=True,
            ),
            self.auth_service,
            google_identity,
        )

        google_identity.verify.assert_called_once_with("x" * 100)
        self.auth_service.authenticate_google.assert_called_once_with(identity)
        self.assertEqual(result.access_token, "google-token")

    def test_invalid_google_credential_returns_unauthorized(self):
        google_identity = Mock()
        google_identity.verify.side_effect = GoogleIdentityError()

        with self.assertRaises(HTTPException) as context:
            google_login(
                GoogleLoginRequest(
                    credential="x" * 100,
                    accept_terms=True,
                ),
                self.auth_service,
                google_identity,
            )

        self.assertEqual(context.exception.status_code, 401)
        self.auth_service.authenticate_google.assert_not_called()

    def test_unconfigured_google_login_returns_service_unavailable(self):
        google_identity = Mock()
        google_identity.verify.side_effect = (
            GoogleIdentityNotConfiguredError()
        )

        with self.assertRaises(HTTPException) as context:
            google_login(
                GoogleLoginRequest(
                    credential="x" * 100,
                    accept_terms=True,
                ),
                self.auth_service,
                google_identity,
            )

        self.assertEqual(context.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
