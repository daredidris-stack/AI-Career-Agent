import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.support_service import (
    SupportService,
    SupportTicketNotFoundError,
)


class SupportServiceTests(unittest.TestCase):
    def test_create_ticket_normalizes_user_text(self):
        repository = Mock()
        repository.create_ticket.return_value = SimpleNamespace(
            id=1,
            category="feedback",
            subject="Feature request",
            message="Please add this.",
            status="new",
            created_at=None,
            updated_at=None,
        )
        service = SupportService(repository)

        result = service.create_ticket(
            7,
            "feedback",
            "  Feature request  ",
            "  Please add this.  ",
        )

        repository.create_ticket.assert_called_once_with(
            user_id=7,
            category="feedback",
            subject="Feature request",
            message="Please add this.",
        )
        self.assertEqual(result["status"], "new")

    def test_update_missing_ticket_raises_not_found(self):
        repository = Mock()
        repository.get_ticket.return_value = None

        with self.assertRaises(SupportTicketNotFoundError):
            SupportService(repository).update_ticket(
                99,
                "resolved",
                "Done",
                1,
                "admin@example.com",
                "request-1",
            )

    def test_update_ticket_records_metadata_without_note_content(self):
        repository = Mock()
        ticket = SimpleNamespace(
            id=4,
            user_id=9,
            category="account",
            subject="Help",
            message="Please help with my account.",
            status="new",
            admin_note=None,
            created_at=None,
            updated_at=None,
        )
        repository.get_ticket.return_value = ticket
        repository.save_ticket_with_audit.return_value = (ticket, Mock())

        result = SupportService(repository).update_ticket(
            4,
            "resolved",
            "  Private resolution detail  ",
            2,
            "Admin@Example.com",
            "r" * 100,
        )

        self.assertEqual(result["status"], "resolved")
        call = repository.save_ticket_with_audit.call_args
        self.assertEqual(call.kwargs["actor_email"], "admin@example.com")
        self.assertEqual(call.kwargs["request_id"], "r" * 64)
        self.assertEqual(call.kwargs["details"], {
            "previous_status": "new",
            "new_status": "resolved",
            "previous_note_present": False,
            "new_note_present": True,
        })
        self.assertNotIn(
            "Private resolution detail",
            str(call.kwargs["details"]),
        )

    def test_operations_summary_exposes_only_configuration_status(self):
        repository = Mock()
        repository.operations_metrics.return_value = {"users": {"total": 3}}

        result = SupportService(repository).operations_summary()

        self.assertEqual(result["metrics"]["users"]["total"], 3)
        self.assertEqual(
            set(result["configuration"]),
            {
                "google_sign_in",
                "email_delivery",
                "job_alert_emails",
                "resume_malware_scanning",
                "billing",
            },
        )


if __name__ == "__main__":
    unittest.main()
