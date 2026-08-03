import unittest
from datetime import UTC, datetime
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.services.job_alert_service import (
    InvalidUnsubscribeTokenError,
    JobAlertService,
)


class JobAlertServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.email = Mock()
        self.email.configured = True
        self.service = JobAlertService(
            self.repository,
            self.email,
            signing_secret="test-secret",
        )
        self.search = SimpleNamespace(
            id=4,
            name="Platform roles",
            alert_frequency="daily",
            alert_timezone="UTC",
            email_alerts_enabled=False,
            next_alert_at=None,
            last_email_at=None,
            created_at=None,
            updated_at=None,
            filters_json='{"keyword": "Platform Engineer"}',
            new_match_count=0,
            last_result_count=0,
            last_run_at=None,
        )
        self.user = SimpleNamespace(
            id=7,
            email="person@example.com",
            is_email_verified=True,
        )

    @patch("backend.services.job_alert_service.JOB_ALERT_EMAIL_ENABLED", True)
    def test_update_preferences_requires_explicit_available_verified_email(self):
        self.repository.get_search.return_value = self.search
        self.repository.save_search.side_effect = lambda item: item

        result = self.service.update_preferences(
            self.user,
            4,
            True,
            "weekly",
            "America/Mexico_City",
        )

        self.assertTrue(result["email_alerts_enabled"])
        self.assertEqual(result["alert_frequency"], "weekly")
        self.assertEqual(result["alert_timezone"], "America/Mexico_City")
        self.assertIsNotNone(result["next_alert_at"])

    @patch("backend.services.job_alert_service.JOB_ALERT_EMAIL_ENABLED", True)
    def test_update_preferences_rejects_unverified_email(self):
        self.repository.get_search.return_value = self.search
        self.user.is_email_verified = False

        with self.assertRaisesRegex(ValueError, "Verify"):
            self.service.update_preferences(
                self.user,
                4,
                True,
                "daily",
                "UTC",
            )

    def test_unsubscribe_token_roundtrip_and_tamper_detection(self):
        token = self.service.create_unsubscribe_token(7, 4)

        self.assertEqual(
            self.service.decode_unsubscribe_token(token),
            (7, 4),
        )
        with self.assertRaises(InvalidUnsubscribeTokenError):
            self.service.decode_unsubscribe_token(f"{token}x")

    @patch("backend.services.job_alert_service.JOB_ALERT_EMAIL_ENABLED", True)
    def test_send_records_delivery_and_unsubscribe_header(self):
        job = {
            "title": "Platform Engineer",
            "company": "Example",
            "source": "Greenhouse",
            "source_job_id": "job-1",
            "listing_url": "https://jobs.example.com/job-1",
        }
        delivery = SimpleNamespace(
            status="pending",
            match_count=1,
            error_code=None,
            sent_at=None,
        )
        self.repository.get_delivery_by_batch.return_value = None
        self.repository.create_delivery.return_value = delivery
        self.repository.save_delivery.side_effect = lambda item: item
        self.repository.save_search.side_effect = lambda item: item
        self.email.send.return_value = True

        sent = self.service.send_matches(
            self.search,
            self.user,
            [job],
        )

        self.assertTrue(sent)
        self.assertEqual(delivery.status, "sent")
        self.assertIsNotNone(delivery.sent_at)
        headers = self.email.send.call_args.kwargs["headers"]
        self.assertIn("/email-preferences?token=", headers["List-Unsubscribe"])
        self.assertIsNotNone(self.search.last_email_at)

    def test_next_delivery_uses_configured_local_hour(self):
        result = self.service.next_delivery_at(
            "daily",
            "America/Mexico_City",
            now=datetime(2026, 7, 29, 13, 30, tzinfo=UTC),
        )

        self.assertEqual(result, datetime(2026, 7, 29, 14, 0))


if __name__ == "__main__":
    unittest.main()
