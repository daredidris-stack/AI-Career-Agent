from sqlalchemy import Column, DateTime, Integer, String, Text, event

from backend.core.time import utc_now
from backend.database.database import Base


class AdminAuditEvent(Base):
    __tablename__ = "admin_audit_events"

    id = Column(Integer, primary_key=True, index=True)
    actor_user_id = Column(Integer, nullable=False, index=True)
    actor_email = Column(String(320), nullable=False)
    action = Column(String(100), nullable=False, index=True)
    target_type = Column(String(100), nullable=False)
    target_id = Column(String(100), nullable=True)
    request_id = Column(String(64), nullable=True, index=True)
    details_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=utc_now, index=True)


def _reject_audit_mutation(*_args, **_kwargs):
    raise RuntimeError("Administrator audit events are append-only.")


event.listen(AdminAuditEvent, "before_update", _reject_audit_mutation)
event.listen(AdminAuditEvent, "before_delete", _reject_audit_mutation)
