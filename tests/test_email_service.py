import unittest
from unittest.mock import Mock, patch

import requests

from backend.services.email_service import EmailService


class EmailServiceTests(unittest.TestCase):
    @patch("backend.services.email_service.BREVO_API_KEY", "")
    @patch("backend.services.email_service.SMTP_FROM_EMAIL", "sender@example.com")
    @patch("backend.services.email_service.SMTP_HOST", "smtp.example.com")
    @patch("backend.services.email_service.SMTP_PASSWORD", "password")
    @patch("backend.services.email_service.SMTP_USERNAME", "username")
    @patch("backend.services.email_service.smtplib.SMTP")
    def test_send_uses_smtp_and_allowlisted_unsubscribe_header(
        self,
        smtp_class,
    ):
        smtp = Mock()
        smtp_class.return_value.__enter__.return_value = smtp

        sent = EmailService().send(
            "person@example.com",
            "New jobs",
            "Body",
            headers={
                "List-Unsubscribe": "<https://app.example.com/preferences>",
                "X-Unsafe": "ignored",
            },
        )

        self.assertTrue(sent)
        smtp.login.assert_called_once_with("username", "password")
        message = smtp.send_message.call_args.args[0]
        self.assertEqual(
            message["List-Unsubscribe"],
            "<https://app.example.com/preferences>",
        )
        self.assertIsNone(message["X-Unsafe"])

    @patch("backend.services.email_service.EMAIL_FROM_NAME", "NextHire AI")
    @patch("backend.services.email_service.SMTP_FROM_EMAIL", "sender@gmail.com")
    @patch("backend.services.email_service.BREVO_API_KEY", "brevo-secret")
    @patch("backend.services.email_service.requests.post")
    def test_send_prefers_brevo_https_api(self, post):
        response = Mock()
        post.return_value = response

        sent = EmailService().send(
            "person@example.com",
            "Reset your password",
            "Body",
            headers={
                "List-Unsubscribe": "<https://app.example.com/preferences>",
                "X-Unsafe": "ignored",
            },
        )

        self.assertTrue(sent)
        response.raise_for_status.assert_called_once_with()
        request = post.call_args
        self.assertEqual(
            request.kwargs["json"],
            {
                "sender": {
                    "name": "NextHire AI",
                    "email": "sender@gmail.com",
                },
                "to": [{"email": "person@example.com"}],
                "subject": "Reset your password",
                "textContent": "Body",
                "headers": {
                    "List-Unsubscribe": (
                        "<https://app.example.com/preferences>"
                    )
                },
            },
        )
        self.assertEqual(request.kwargs["timeout"], 15)
        self.assertEqual(
            request.kwargs["headers"]["api-key"],
            "brevo-secret",
        )

    @patch("backend.services.email_service.SMTP_FROM_EMAIL", "sender@gmail.com")
    @patch("backend.services.email_service.BREVO_API_KEY", "brevo-secret")
    @patch("backend.services.email_service.requests.post")
    def test_send_returns_false_when_brevo_is_unavailable(self, post):
        post.side_effect = requests.RequestException()

        with self.assertLogs(
            "backend.services.email_service",
            level="ERROR",
        ):
            sent = EmailService().send(
                "person@example.com",
                "Subject",
                "Body",
            )

        self.assertFalse(sent)


if __name__ == "__main__":
    unittest.main()
