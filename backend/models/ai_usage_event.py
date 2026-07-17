from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from backend.core.time import utc_now
from backend.database.database import Base


class AIUsageEvent(Base):
    __tablename__ = "ai_usage_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    feature = Column(String, nullable=False, index=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        index=True,
    )
