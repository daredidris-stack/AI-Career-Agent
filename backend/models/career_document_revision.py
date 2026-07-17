from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from backend.core.time import utc_now
from backend.database.database import Base


class CareerDocumentRevision(Base):
    __tablename__ = "career_document_revisions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(
        Integer,
        ForeignKey("career_documents.id"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=utc_now)
