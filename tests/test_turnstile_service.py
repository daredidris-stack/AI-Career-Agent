import unittest
from unittest.mock import Mock, patch

import requests

from backend.services.turnstile_service import (
    SITEVERIFY_URL,
    TurnstileService,
    TurnstileUnavailableError,
    TurnstileVerificationError,
)


class TurnstileServiceTests(unittest.TestCase):
    @patch("backend.services.turnstile_service.requests.post")
    def test_missing_secret_disables_validation(self, mock_post):
        service = TurnstileService(secret_key="")

        service.verify(None, expected_action="login")

        mock_post.assert_not_called()

    @patch("backend.services.turnstile_service.requests.post")
    def test_validates_token_action_and_hostname(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "success": True,
            "action": "login",
            "hostname": "careers.example.com",
        }
        mock_post.return_value = response
        service = TurnstileService(
            secret_key="secret",
            allowed_hostnames=["careers.example.com"],
        )

        service.verify("challenge-token", expected_action="login")

        mock_post.assert_called_once_with(
            SITEVERIFY_URL,
            data={"secret": "secret", "response": "challenge-token"},
            timeout=10,
        )
        response.raise_for_status.assert_called_once()

    @patch("backend.services.turnstile_service.requests.post")
    def test_rejects_failed_challenge(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "success": False,
            "error-codes": ["invalid-input-response"],
        }
        mock_post.return_value = response
        service = TurnstileService(secret_key="secret")

        with self.assertRaises(TurnstileVerificationError):
            service.verify("bad-token", expected_action="login")

    @patch("backend.services.turnstile_service.requests.post")
    def test_rejects_wrong_action_or_hostname(self, mock_post):
        response = Mock()
        mock_post.return_value = response
        service = TurnstileService(
            secret_key="secret",
            allowed_hostnames=["careers.example.com"],
        )

        response.json.return_value = {
            "success": True,
            "action": "register",
            "hostname": "careers.example.com",
        }
        with self.assertRaises(TurnstileVerificationError):
            service.verify("token", expected_action="login")

        response.json.return_value = {
            "success": True,
            "action": "login",
            "hostname": "attacker.example.com",
        }
        with self.assertRaises(TurnstileVerificationError):
            service.verify("token", expected_action="login")

    @patch("backend.services.turnstile_service.requests.post")
    def test_allows_cloudflare_test_response_outside_production(
        self,
        mock_post,
    ):
        response = Mock()
        response.json.return_value = {
            "success": True,
            "hostname": "localhost",
            "action": "login",
        }
        mock_post.return_value = response
        service = TurnstileService(
            secret_key="1x0000000000000000000000000000000AA",
            allowed_hostnames=["localhost"],
            allow_test_keys=True,
        )

        service.verify("dummy-token", expected_action="login")

    @patch("backend.services.turnstile_service.requests.post")
    def test_rejects_cloudflare_test_response_in_production(
        self,
        mock_post,
    ):
        response = Mock()
        mock_post.return_value = response
        service = TurnstileService(
            secret_key="1x0000000000000000000000000000000AA",
            allowed_hostnames=["careers.example.com"],
            allow_test_keys=False,
        )

        with self.assertRaises(TurnstileVerificationError):
            service.verify("dummy-token", expected_action="login")

        mock_post.assert_not_called()

    @patch("backend.services.turnstile_service.requests.post")
    def test_success_requires_an_allowed_hostname(self, mock_post):
        response = Mock()
        response.json.return_value = {
            "success": True,
            "action": "login",
            "hostname": "careers.example.com",
        }
        mock_post.return_value = response
        service = TurnstileService(
            secret_key="secret",
            allowed_hostnames=[],
        )

        with self.assertRaises(TurnstileVerificationError):
            service.verify("challenge-token", expected_action="login")

    @patch("backend.services.turnstile_service.requests.post")
    def test_provider_failure_is_reported_without_request_details(
        self,
        mock_post,
    ):
        mock_post.side_effect = requests.ConnectionError(
            "request included a sensitive secret"
        )
        service = TurnstileService(secret_key="sensitive-secret")

        with self.assertRaises(TurnstileUnavailableError) as context:
            service.verify("token", expected_action="login")

        self.assertNotIn("sensitive", str(context.exception))


if __name__ == "__main__":
    unittest.main()
