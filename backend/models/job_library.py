from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)

from backend.core.time import utc_now
from backend.database.database import Base


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "job_key",
            name="uq_saved_jobs_user_job_key",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    job_key = Column(String(64), nullable=False, index=True)
    title = Column(String(300), nullable=False)
    company = Column(String(300), nullable=False)
    source = Column(String(100), nullable=True)
    source_job_id = Column(String(300), nullable=True)
    location = Column(String(500), nullable=True)
    listing_url = Column(Text, nullable=True)
    apply_url = Column(Text, nullable=True)
    job_data_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class SavedSearch(Base):
    __tablename__ = "saved_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(120), nullable=False)
    filters_json = Column(Text, nullable=False, default="{}")
    seen_job_keys_json = Column(Text, nullable=False, default="[]")
    new_match_count = Column(Integer, nullable=False, default=0)
    last_result_count = Column(Integer, nullable=False, default=0)
    last_run_at = Column(DateTime, nullable=True)
    email_alerts_enabled = Column(Boolean, nullable=False, default=False)
    alert_frequency = Column(String(20), nullable=False, default="daily")
    alert_timezone = Column(String(64), nullable=False, default="UTC")
    next_alert_at = Column(DateTime, nullable=True, index=True)
    last_email_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class JobAlertDelivery(Base):
    __tablename__ = "job_alert_deliveries"
    __table_args__ = (
        UniqueConstraint(
            "saved_search_id",
            "batch_key",
            name="uq_job_alert_deliveries_search_batch",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    saved_search_id = Column(
        Integer,
        ForeignKey("saved_searches.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    batch_key = Column(String(64), nullable=False)
    status = Column(String(30), nullable=False, index=True)
    match_count = Column(Integer, nullable=False, default=0)
    error_code = Column(String(100), nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    sent_at = Column(DateTime, nullable=True)
