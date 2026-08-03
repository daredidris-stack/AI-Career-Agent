import unittest
from unittest.mock import Mock, patch

from backend.services.email_service import EmailService


class EmailServiceTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
