from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    DateTime,
)

from backend.core.time import utc_now
from backend.database.database import Base


class Profile(Base):

    __tablename__ = "profiles"


    id = Column(
        Integer,
        primary_key=True,
        index=True
    )


    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )


    # -------------------------
    # Contact Information
    # -------------------------

    phone = Column(
        String,
        nullable=True
    )


    country = Column(
        String,
        nullable=True
    )


    state = Column(
        String,
        nullable=True
    )


    city = Column(
        String,
        nullable=True
    )


    # -------------------------
    # Career
    # -------------------------

    current_role = Column(
        String,
        nullable=True
    )


    target_role = Column(
        String,
        nullable=True
    )


    years_experience = Column(
        Integer,
        nullable=True
    )


    professional_summary = Column(
        Text,
        nullable=True
    )


    # -------------------------
    # Skills
    # -------------------------

    technical_skills = Column(
        Text,
        nullable=True
    )


    soft_skills = Column(
        Text,
        nullable=True
    )


    # -------------------------
    # Professional Links
    # -------------------------

    linkedin = Column(
        String,
        nullable=True
    )


    github = Column(
        String,
        nullable=True
    )


    portfolio = Column(
        String,
        nullable=True
    )


    # -------------------------
    # Career Preferences
    # -------------------------

    preferred_job_type = Column(
        String,
        nullable=True
    )


    preferred_work_mode = Column(
        String,
        nullable=True
    )


    # -------------------------
    # Timestamps
    # -------------------------

    created_at = Column(
        DateTime,
        default=utc_now
    )


    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now
    )
