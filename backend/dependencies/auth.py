from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from backend.auth.jwt_handler import decode_access_token
from backend.core.settings import ADMIN_EMAILS
from backend.models.user import User
from backend.database.database import get_db
from sqlalchemy.orm import Session


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    payload = decode_access_token(token)


    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
        )


    user_id = payload.get("user_id")


    user = (
        db.query(User)
        .filter(User.id == user_id)
        .first()
    )


    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    if payload.get("token_version") != (user.token_version or 0):
        raise HTTPException(
            status_code=401,
            detail="Token has been revoked",
        )


    return user


def is_admin_user(user: User) -> bool:
    return (
        bool(user.is_email_verified)
        and user.email.strip().casefold() in ADMIN_EMAILS
    )


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    if not is_admin_user(current_user):
        raise HTTPException(
            status_code=403,
            detail="Administrator access is required.",
        )
    return current_user
