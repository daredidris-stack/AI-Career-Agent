from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

from backend.auth.jwt_handler import decode_access_token
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


    return user