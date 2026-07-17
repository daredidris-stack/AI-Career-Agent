from datetime import datetime

from sqlalchemy.orm import Session

from backend.models.ai_usage_event import AIUsageEvent
from backend.models.user import User


class AIUsageRepository:
    def __init__(self, db: Session):
        self.db = db

    def count_since(self, user_id: int, since: datetime) -> int:
        return self.db.query(AIUsageEvent).filter(
            AIUsageEvent.user_id == user_id,
            AIUsageEvent.created_at >= since,
        ).count()

    def record(self, user_id: int, feature: str) -> AIUsageEvent:
        event = AIUsageEvent(user_id=user_id, feature=feature)
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_plan(self, user_id: int) -> str:
        value = self.db.query(User.plan).filter(User.id == user_id).scalar()
        return value or "free"
