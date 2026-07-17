from datetime import timedelta

from backend.core.settings import (
    AI_PRO_REQUESTS_PER_DAY,
    AI_PRO_REQUESTS_PER_HOUR,
    AI_REQUESTS_PER_DAY,
    AI_REQUESTS_PER_HOUR,
)
from backend.core.time import utc_now
from backend.repositories.ai_usage_repository import AIUsageRepository


class AIUsageLimitError(Exception):
    pass


class AIUsageService:
    def __init__(self, repository: AIUsageRepository):
        self.repository = repository

    def reserve(self, user_id: int, feature: str) -> None:
        now = utc_now()
        is_pro = self.repository.get_plan(user_id) == "pro"
        hourly_limit = AI_PRO_REQUESTS_PER_HOUR if is_pro else AI_REQUESTS_PER_HOUR
        daily_limit = AI_PRO_REQUESTS_PER_DAY if is_pro else AI_REQUESTS_PER_DAY
        if self.repository.count_since(
            user_id, now - timedelta(hours=1)
        ) >= hourly_limit:
            raise AIUsageLimitError(
                "Hourly AI usage limit reached. Please try again later."
            )
        if self.repository.count_since(
            user_id, now - timedelta(days=1)
        ) >= daily_limit:
            raise AIUsageLimitError(
                "Daily AI usage limit reached. Please try again tomorrow."
            )
        self.repository.record(user_id, feature)


def reserve_ai_usage(usage, user_id: int, feature: str) -> None:
    """Reserve usage when called through FastAPI dependency injection."""
    reserve = getattr(usage, "reserve", None)
    if callable(reserve):
        reserve(user_id, feature)
