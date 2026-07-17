from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from backend.core.time import utc_now
from backend.database.database import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )
    filename = Column(String, nullable=False)
    resume_score = Column(Integer, nullable=False)
    ats_score = Column(Integer, nullable=False)
    strengths = Column(Text, nullable=False, default="[]")
    improvements = Column(Text, nullable=False, default="[]")
    extracted_skills = Column(Text, nullable=False, default="[]")
    created_at = Column(DateTime, default=utc_now, nullable=False)
