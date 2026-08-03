import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.models.schemas import SupportTicketCreate, SupportTicketUpdate
from backend.routes.support import (
    create_support_ticket,
    list_support_tickets,
    update_support_ticket,
)
from backend.services.support_service import SupportTicketNotFoundError


class SupportRouteTests(unittest.TestCase):
    def test_create_ticket_passes_authenticated_owner(self):
        service = Mock()
        service.create_ticket.return_value = {"id": 2}
        request = SupportTicketCreate(
            category="feedback",
            subject="Feature request",
            message="Please add a calendar view.",
        )

        result = create_support_ticket(
            request,
            SimpleNamespace(id=7),
            service,
        )

        self.assertEqual(result, {"id": 2})
        service.create_ticket.assert_called_once_with(
            7,
            "feedback",
            "Feature request",
            "Please add a calendar view.",
        )

    def test_invalid_admin_ticket_filter_returns_400(self):
        with self.assertRaises(HTTPException) as context:
            list_support_tickets(
                "invalid",
                SimpleNamespace(id=1),
                Mock(),
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_update_missing_ticket_returns_404(self):
        service = Mock()
        service.update_ticket.side_effect = SupportTicketNotFoundError()
        request = SupportTicketUpdate(
            status="resolved",
            admin_note="Completed.",
        )

        with self.assertRaises(HTTPException) as context:
            update_support_ticket(
                5,
                request,
                SimpleNamespace(
                    state=SimpleNamespace(request_id="request-1"),
                ),
                SimpleNamespace(id=1, email="admin@example.com"),
                service,
            )

        self.assertEqual(context.exception.status_code, 404)
        service.update_ticket.assert_called_once_with(
            5,
            "resolved",
            "Completed.",
            1,
            "admin@example.com",
            "request-1",
        )


if __name__ == "__main__":
    unittest.main()
