from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text

from backend.core.time import utc_now
from backend.database.database import Base


class InterviewPracticeAttempt(Base):
    __tablename__ = "interview_practice_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(200), nullable=False)
    interview_type = Column(String(100), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)
    rubric_json = Column(Text, nullable=False, default="{}")
    created_at = Column(DateTime, nullable=False, default=utc_now)
