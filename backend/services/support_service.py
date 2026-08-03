import json
from typing import Any

from backend.core.settings import (
    APP_ENV,
    APP_RELEASE,
    GOOGLE_CLIENT_ID,
    CLAMAV_HOST,
    JOB_ALERT_EMAIL_ENABLED,
    MALWARE_SCANNING_ENABLED,
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    STRIPE_PRO_PRICE_ID,
    STRIPE_SECRET_KEY,
    STRIPE_WEBHOOK_SECRET,
)
from backend.repositories.support_repository import SupportRepository


class SupportTicketNotFoundError(Exception):
    pass


class SupportService:
    def __init__(self, repository: SupportRepository):
        self.repository = repository

    def create_ticket(
        self,
        user_id: int,
        category: str,
        subject: str,
        message: str,
    ) -> dict[str, Any]:
        ticket = self.repository.create_ticket(
            user_id=user_id,
            category=category,
            subject=subject.strip(),
            message=message.strip(),
        )
        return self._user_ticket_response(ticket)

    def list_user_tickets(self, user_id: int) -> list[dict[str, Any]]:
        return [
            self._user_ticket_response(ticket)
            for ticket in self.repository.list_user_tickets(user_id)
        ]

    def list_admin_tickets(
        self,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        return [
            self._admin_ticket_response(ticket, email)
            for ticket, email in self.repository.list_all_tickets(status)
        ]

    def update_ticket(
        self,
        ticket_id: int,
        status: str,
        admin_note: str | None,
        actor_user_id: int,
        actor_email: str,
        request_id: str | None,
    ) -> dict[str, Any]:
        ticket = self.repository.get_ticket(ticket_id)
        if not ticket:
            raise SupportTicketNotFoundError()
        previous_status = ticket.status
        previous_note_present = bool(ticket.admin_note)
        ticket.status = status
        ticket.admin_note = (
            admin_note.strip()
            if admin_note and admin_note.strip()
            else None
        )
        saved, _audit_event = self.repository.save_ticket_with_audit(
            ticket,
            actor_user_id=actor_user_id,
            actor_email=actor_email.strip().casefold(),
            action="support_ticket.updated",
            request_id=(
                str(request_id).strip()[:64]
                if request_id
                else None
            ),
            details={
                "previous_status": previous_status,
                "new_status": ticket.status,
                "previous_note_present": previous_note_present,
                "new_note_present": bool(ticket.admin_note),
            },
        )
        return self._admin_ticket_response(saved, None)

    def list_audit_events(self, limit: int = 100) -> list[dict[str, Any]]:
        return [
            self._audit_event_response(event)
            for event in self.repository.list_audit_events(limit)
        ]

    def operations_summary(self) -> dict[str, Any]:
        return {
            "environment": APP_ENV,
            "release": APP_RELEASE,
            "configuration": {
                "google_sign_in": bool(GOOGLE_CLIENT_ID),
                "email_delivery": bool(SMTP_HOST and SMTP_FROM_EMAIL),
                "job_alert_emails": bool(
                    JOB_ALERT_EMAIL_ENABLED
                    and SMTP_HOST
                    and SMTP_FROM_EMAIL
                ),
                "resume_malware_scanning": bool(
                    MALWARE_SCANNING_ENABLED and CLAMAV_HOST
                ),
                "billing": bool(
                    STRIPE_SECRET_KEY
                    and STRIPE_WEBHOOK_SECRET
                    and STRIPE_PRO_PRICE_ID
                ),
            },
            "metrics": self.repository.operations_metrics(),
        }

    @staticmethod
    def _user_ticket_response(ticket) -> dict[str, Any]:
        return {
            "id": ticket.id,
            "category": ticket.category,
            "subject": ticket.subject,
            "message": ticket.message,
            "status": ticket.status,
            "created_at": ticket.created_at,
            "updated_at": ticket.updated_at,
        }

    @classmethod
    def _admin_ticket_response(
        cls,
        ticket,
        email: str | None,
    ) -> dict[str, Any]:
        return {
            **cls._user_ticket_response(ticket),
            "user_id": ticket.user_id,
            "user_email": email,
            "admin_note": ticket.admin_note,
        }

    @staticmethod
    def _audit_event_response(event) -> dict[str, Any]:
        try:
            details = json.loads(event.details_json or "{}")
        except (TypeError, json.JSONDecodeError):
            details = {}
        return {
            "id": event.id,
            "actor_user_id": event.actor_user_id,
            "actor_email": event.actor_email,
            "action": event.action,
            "target_type": event.target_type,
            "target_id": event.target_id,
            "request_id": event.request_id,
            "details": details if isinstance(details, dict) else {},
            "created_at": event.created_at,
        }
