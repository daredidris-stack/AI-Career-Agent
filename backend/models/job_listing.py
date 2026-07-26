from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    String,
    Text,
)

from backend.core.time import utc_now
from backend.database.database import Base


class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    dedupe_key = Column(String(64), nullable=False, unique=True, index=True)
    source = Column(String, nullable=False, index=True)
    source_job_id = Column(String, nullable=True)
    title = Column(String, nullable=False, index=True)
    company = Column(String, nullable=False, index=True)
    location = Column(String, nullable=True, index=True)
    description = Column(Text, nullable=True)
    listing_url = Column(Text, nullable=True)
    apply_url = Column(Text, nullable=True)
    job_type = Column(String, nullable=True)
    workplace_type = Column(String, nullable=True)
    skills_json = Column(Text, nullable=False, default="[]")
    salary = Column(String, nullable=True)
    salary_min = Column(Float, nullable=True)
    salary_max = Column(Float, nullable=True)
    salary_currency = Column(String, nullable=True)
    visa_sponsorship = Column(Boolean, nullable=True)
    published_at = Column(DateTime, nullable=True, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    source_metadata_json = Column(Text, nullable=False, default="{}")
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    first_seen_at = Column(DateTime, nullable=False, default=utc_now)
    last_seen_at = Column(DateTime, nullable=False, default=utc_now, index=True)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )


class JobSyncState(Base):
    __tablename__ = "job_sync_states"

    id = Column(Integer, primary_key=True, index=True)
    sync_key = Column(String(64), nullable=False, unique=True, index=True)
    provider = Column(String, nullable=False, index=True)
    keyword = Column(String, nullable=False)
    location = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    last_attempt_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    next_sync_at = Column(DateTime, nullable=True, index=True)
    jobs_fetched = Column(Integer, nullable=False, default=0)
    jobs_created = Column(Integer, nullable=False, default=0)
    jobs_updated = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
