from datetime import datetime

from backend.core.time import utc_now
from backend.models.user import User
from backend.repositories.user_data_repository import UserDataRepository


class UserDataService:
    def __init__(self, repository: UserDataRepository):
        self.repository = repository

    def export_for_user(self, user: User) -> dict:
        snapshot = self.repository.snapshot(user.id)
        return {
            "exported_at": utc_now().isoformat() + "Z",
            "account": {
                "id": user.id,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "created_at": self._value(user.created_at),
                "is_email_verified": user.is_email_verified,
                "terms_accepted_at": self._value(
                    getattr(user, "terms_accepted_at", None)
                ),
                "terms_version": getattr(user, "terms_version", None),
            },
            **{
                key: self._serialize(value)
                for key, value in snapshot.items()
            },
        }

    @classmethod
    def _serialize(cls, value):
        if value is None:
            return None
        if isinstance(value, list):
            return [cls._serialize(item) for item in value]
        return {
            column.name: cls._value(getattr(value, column.name))
            for column in value.__table__.columns
            if column.name != "user_id"
        }

    @staticmethod
    def _value(value):
        return value.isoformat() + "Z" if isinstance(value, datetime) else value
