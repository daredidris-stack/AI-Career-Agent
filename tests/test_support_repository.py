import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.database.database import Base
from backend.models.admin_audit_event import AdminAuditEvent
from backend.models.job_application import JobApplication
from backend.models.support_ticket import SupportTicket
from backend.models.user import User
from backend.repositories.support_repository import SupportRepository


class SupportRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine(
            "sqlite://",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()
        self.first = User(email="first@example.com", password_hash="hash")
        self.second = User(email="second@example.com", password_hash="hash")
        self.db.add_all([self.first, self.second])
        self.db.commit()
        self.repository = SupportRepository(self.db)

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_user_ticket_list_is_owner_scoped(self):
        self.repository.create_ticket(
            self.first.id,
            "jobs",
            "First request",
            "The first user needs help with a job.",
        )
        self.repository.create_ticket(
            self.second.id,
            "account",
            "Private request",
            "The second user needs private help.",
        )

        result = self.repository.list_user_tickets(self.first.id)

        self.assertEqual([ticket.subject for ticket in result], ["First request"])

    def test_operations_metrics_group_application_and_support_statuses(self):
        self.db.add_all([
            JobApplication(
                user_id=self.first.id,
                company="Example",
                role="Engineer",
                status="saved",
            ),
            SupportTicket(
                user_id=self.first.id,
                category="feedback",
                subject="Feature request",
                message="Please add a useful feature to the application.",
                status="new",
            ),
        ])
        self.db.commit()

        result = self.repository.operations_metrics()

        self.assertEqual(result["users"]["total"], 2)
        self.assertEqual(result["applications"], {"saved": 1})
        self.assertEqual(result["support"], {"new": 1})

    def test_ticket_update_and_audit_event_commit_together(self):
        ticket = self.repository.create_ticket(
            self.first.id,
            "account",
            "Account help",
            "Please help with this account issue.",
        )
        ticket.status = "resolved"
        saved, event = self.repository.save_ticket_with_audit(
            ticket,
            actor_user_id=self.second.id,
            actor_email=self.second.email,
            action="support_ticket.updated",
            request_id="request-123",
            details={
                "previous_status": "new",
                "new_status": "resolved",
                "previous_note_present": False,
                "new_note_present": False,
            },
        )

        self.assertEqual(saved.status, "resolved")
        self.assertEqual(event.target_id, str(ticket.id))
        self.assertNotIn("Please help", event.details_json)
        self.assertEqual(
            [item.id for item in self.repository.list_audit_events()],
            [event.id],
        )

    def test_audit_event_cannot_be_changed_through_orm(self):
        event = AdminAuditEvent(
            actor_user_id=self.first.id,
            actor_email=self.first.email,
            action="support_ticket.updated",
            target_type="support_ticket",
            target_id="1",
            details_json="{}",
        )
        self.db.add(event)
        self.db.commit()

        event.action = "changed"
        with self.assertRaisesRegex(RuntimeError, "append-only"):
            self.db.commit()
        self.db.rollback()

        stored = self.db.query(AdminAuditEvent).one()
        self.assertEqual(stored.action, "support_ticket.updated")


if __name__ == "__main__":
    unittest.main()
