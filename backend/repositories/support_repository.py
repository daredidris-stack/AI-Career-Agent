import json
from datetime import timedelta

from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.core.time import utc_now
from backend.models.admin_audit_event import AdminAuditEvent
from backend.models.ai_usage_event import AIUsageEvent
from backend.models.job_application import JobApplication
from backend.models.job_library import (
    JobAlertDelivery,
    SavedJob,
    SavedSearch,
)
from backend.models.job_listing import JobListing
from backend.models.support_ticket import SupportTicket
from backend.models.interview_practice import InterviewPracticeAttempt
from backend.models.user import User


class SupportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_ticket(
        self,
        user_id: int,
        category: str,
        subject: str,
        message: str,
    ) -> SupportTicket:
        ticket = SupportTicket(
            user_id=user_id,
            category=category,
            subject=subject,
            message=message,
        )
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def list_user_tickets(self, user_id: int) -> list[SupportTicket]:
        return (
            self.db.query(SupportTicket)
            .filter(SupportTicket.user_id == user_id)
            .order_by(SupportTicket.created_at.desc())
            .all()
        )

    def get_ticket(self, ticket_id: int) -> SupportTicket | None:
        return (
            self.db.query(SupportTicket)
            .filter(SupportTicket.id == ticket_id)
            .first()
        )

    def list_all_tickets(
        self,
        status: str | None = None,
        limit: int = 100,
    ):
        query = self.db.query(SupportTicket, User.email).join(
            User,
            User.id == SupportTicket.user_id,
        )
        if status:
            query = query.filter(SupportTicket.status == status)
        return (
            query.order_by(SupportTicket.created_at.desc())
            .limit(limit)
            .all()
        )

    def save_ticket(self, ticket: SupportTicket) -> SupportTicket:
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket

    def save_ticket_with_audit(
        self,
        ticket: SupportTicket,
        *,
        actor_user_id: int,
        actor_email: str,
        action: str,
        request_id: str | None,
        details: dict,
    ) -> tuple[SupportTicket, AdminAuditEvent]:
        audit_event = AdminAuditEvent(
            actor_user_id=actor_user_id,
            actor_email=actor_email,
            action=action,
            target_type="support_ticket",
            target_id=str(ticket.id),
            request_id=request_id,
            details_json=json.dumps(details, sort_keys=True),
        )
        self.db.add_all([ticket, audit_event])
        try:
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            raise
        self.db.refresh(ticket)
        self.db.refresh(audit_event)
        return ticket, audit_event

    def list_audit_events(self, limit: int = 100):
        return (
            self.db.query(AdminAuditEvent)
            .order_by(
                AdminAuditEvent.created_at.desc(),
                AdminAuditEvent.id.desc(),
            )
            .limit(max(1, min(200, limit)))
            .all()
        )

    def operations_metrics(self) -> dict:
        cutoff = utc_now() - timedelta(hours=24)
        return {
            "users": {
                "total": self.db.query(User).count(),
                "verified": self.db.query(User).filter(
                    User.is_email_verified.is_(True)
                ).count(),
            },
            "jobs": {
                "catalog_listings": self.db.query(JobListing).count(),
                "saved_jobs": self.db.query(SavedJob).count(),
                "saved_searches": self.db.query(SavedSearch).count(),
                "email_alert_searches": self.db.query(SavedSearch).filter(
                    SavedSearch.email_alerts_enabled.is_(True)
                ).count(),
            },
            "job_alert_deliveries": self._count_by(
                JobAlertDelivery.status,
                JobAlertDelivery,
            ),
            "applications": self._count_by(
                JobApplication.status,
                JobApplication,
            ),
            "support": self._count_by(
                SupportTicket.status,
                SupportTicket,
            ),
            "ai_requests_last_24_hours": self.db.query(AIUsageEvent).filter(
                AIUsageEvent.created_at >= cutoff
            ).count(),
            "interview_practice_attempts": self.db.query(
                InterviewPracticeAttempt
            ).count(),
            "admin_audit_events": self.db.query(AdminAuditEvent).count(),
        }

    def _count_by(self, column, model) -> dict[str, int]:
        return {
            str(value): int(count)
            for value, count in self.db.query(
                column,
                func.count(model.id),
            ).group_by(column).all()
        }
