from datetime import UTC, datetime, timedelta

from jose import jwt, JWTError

from backend.core.settings import (
    ACCESS_TOKEN_EXPIRE_HOURS,
    JWT_ALGORITHM,
    require_jwt_secret,
)


def create_access_token(data: dict):

    payload = data.copy()

    payload["exp"] = (
        datetime.now(UTC)
        + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )

    return jwt.encode(
        payload,
        require_jwt_secret(),
        algorithm=JWT_ALGORITHM
    )


def decode_access_token(token: str):

    try:

        payload = jwt.decode(
            token,
            require_jwt_secret(),
            algorithms=[JWT_ALGORITHM],
        )

        return payload


    except JWTError:

        return None


def create_action_token(
    user_id: int,
    token_version: int,
    purpose: str,
    expires_minutes: int,
) -> str:
    return jwt.encode(
        {
            "user_id": user_id,
            "token_version": token_version,
            "purpose": purpose,
            "exp": datetime.now(UTC) + timedelta(minutes=expires_minutes),
        },
        require_jwt_secret(),
        algorithm=JWT_ALGORITHM,
    )


def decode_action_token(token: str, purpose: str) -> dict | None:
    payload = decode_access_token(token)
    if not payload or payload.get("purpose") != purpose:
        return None
    return payload
