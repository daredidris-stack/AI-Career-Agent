from datetime import timedelta

from backend.auth.hashing import (
    hash_password,
    verify_password,
)

from backend.auth.jwt_handler import (
    create_access_token,
)
from backend.core.time import utc_now

from backend.repositories.user_repository import UserRepository

from backend.exceptions.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    LoginLockedError,
)


MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15


class AuthService:

    def __init__(
        self,
        repo: UserRepository,
    ):
        self.repo = repo


    def register_user(
        self,
        email: str,
        password: str,
    ):

        existing = self.repo.get_by_email(email)

        if existing:
            raise UserAlreadyExistsError()

        return self.repo.create_user(
            email=email,
            password_hash=hash_password(password),
        )


    def authenticate_user(
        self,
        email: str,
        password: str,
    ):

        user = self.repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        now = utc_now()
        if user.locked_until and user.locked_until > now:
            raise LoginLockedError()

        if user.locked_until:
            user.locked_until = None
            user.failed_login_attempts = 0

        if not verify_password(
            password,
            user.password_hash,
        ):
            user.failed_login_attempts = (
                user.failed_login_attempts or 0
            ) + 1
            if user.failed_login_attempts >= MAX_FAILED_LOGINS:
                user.locked_until = now + timedelta(minutes=LOCK_MINUTES)
            self.repo.save(user)
            if user.locked_until:
                raise LoginLockedError()
            raise InvalidCredentialsError()

        if user.failed_login_attempts or user.locked_until:
            user.failed_login_attempts = 0
            user.locked_until = None
            self.repo.save(user)

        return create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "token_version": user.token_version or 0,
            }
        )

    def delete_account(self, user, password: str) -> None:
        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()
        self.repo.delete_user(user)
