from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from backend.core.time import utc_now
from backend.database.database import Base


class CareerDocument(Base):
    __tablename__ = "career_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    kind = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    source_filename = Column(String, nullable=True)
    job_description = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=utc_now)
    updated_at = Column(
        DateTime,
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
    )
