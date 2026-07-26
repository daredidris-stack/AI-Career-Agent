import unittest
from unittest.mock import patch

from google.auth.exceptions import TransportError

from backend.services.google_identity_service import (
    GoogleIdentityError,
    GoogleIdentityNotConfiguredError,
    GoogleIdentityService,
    GoogleIdentityUnavailableError,
)


class GoogleIdentityServiceTests(unittest.TestCase):
    def test_missing_client_id_disables_google_login(self):
        with self.assertRaises(GoogleIdentityNotConfiguredError):
            GoogleIdentityService(client_id="").verify("credential")

    @patch(
        "backend.services.google_identity_service.id_token.verify_oauth2_token"
    )
    def test_verifies_google_identity_for_expected_client(self, verify_token):
        verify_token.return_value = {
            "sub": "google-user-123",
            "email": "User@Gmail.com",
            "email_verified": True,
            "given_name": "Dare",
            "family_name": "Daniel",
        }

        identity = GoogleIdentityService(
            client_id="client.apps.googleusercontent.com"
        ).verify("credential")

        self.assertEqual(identity.subject, "google-user-123")
        self.assertEqual(identity.email, "user@gmail.com")
        self.assertEqual(identity.first_name, "Dare")
        self.assertTrue(identity.email_authoritative)
        self.assertEqual(
            verify_token.call_args.args[2],
            "client.apps.googleusercontent.com",
        )

    @patch(
        "backend.services.google_identity_service.id_token.verify_oauth2_token"
    )
    def test_google_is_not_authoritative_for_third_party_email(
        self,
        verify_token,
    ):
        verify_token.return_value = {
            "sub": "google-user-123",
            "email": "user@example.com",
            "email_verified": True,
        }

        identity = GoogleIdentityService(
            client_id="client.apps.googleusercontent.com"
        ).verify("credential")

        self.assertFalse(identity.email_authoritative)

    @patch(
        "backend.services.google_identity_service.id_token.verify_oauth2_token"
    )
    def test_workspace_domain_is_authoritative(self, verify_token):
        verify_token.return_value = {
            "sub": "google-user-123",
            "email": "user@example.com",
            "email_verified": True,
            "hd": "Example.com",
        }

        identity = GoogleIdentityService(
            client_id="client.apps.googleusercontent.com"
        ).verify("credential")

        self.assertTrue(identity.email_authoritative)
        self.assertEqual(identity.hosted_domain, "example.com")

    @patch(
        "backend.services.google_identity_service.id_token.verify_oauth2_token"
    )
    def test_rejects_unverified_google_email(self, verify_token):
        verify_token.return_value = {
            "sub": "google-user-123",
            "email": "user@gmail.com",
            "email_verified": False,
        }

        with self.assertRaises(GoogleIdentityError):
            GoogleIdentityService(client_id="client-id").verify("credential")

    @patch(
        "backend.services.google_identity_service.id_token.verify_oauth2_token"
    )
    def test_reports_google_key_fetch_failure(self, verify_token):
        verify_token.side_effect = TransportError("unavailable")

        with self.assertRaises(GoogleIdentityUnavailableError):
            GoogleIdentityService(client_id="client-id").verify("credential")


if __name__ == "__main__":
    unittest.main()
