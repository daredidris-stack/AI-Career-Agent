from sqlalchemy.orm import Session

from backend.core.time import utc_now
from backend.models.refresh_token import RefreshToken


class RefreshTokenRepository:

    def __init__(self, db: Session):
        self.db = db


    def create(self, user_id: int, token_hash: str, expires_at) -> RefreshToken:
        refresh_token = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.db.add(refresh_token)
        self.db.commit()
        self.db.refresh(refresh_token)
        return refresh_token


    def get_by_token_hash(self, token_hash: str):
        return (
            self.db.query(RefreshToken)
            .filter(RefreshToken.token_hash == token_hash)
            .first()
        )


    def revoke(self, token_hash: str) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.token_hash == token_hash
        ).update({RefreshToken.revoked_at: utc_now()})
        self.db.commit()


    def revoke_all_for_user(self, user_id: int) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).update({RefreshToken.revoked_at: utc_now()})
        self.db.commit()


    def cleanup_expired(self) -> None:
        self.db.query(RefreshToken).filter(
            RefreshToken.expires_at < utc_now()
        ).delete(synchronize_session=False)
        self.db.commit()
