from datetime import timedelta

from backend.auth.hashing import (
    hash_password,
    verify_password,
)

from backend.auth.jwt_handler import (
    create_access_token,
    create_action_token,
    decode_action_token,
)
from backend.core.settings import (
    FRONTEND_URL,
    LEGAL_TERMS_VERSION,
    REQUIRE_EMAIL_VERIFICATION,
)
from backend.core.time import utc_now

from backend.repositories.user_repository import UserRepository

from backend.exceptions.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    LoginLockedError,
    EmailNotVerifiedError,
    InvalidActionTokenError,
)
from backend.services.email_service import EmailService


MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15


class AuthService:

    def __init__(
        self,
        repo: UserRepository,
        email_service: EmailService | None = None,
    ):
        self.repo = repo
        self.email_service = email_service or EmailService()


    def register_user(
        self,
        email: str,
        password: str,
    ):

        existing = self.repo.get_by_email(email)

        if existing:
            raise UserAlreadyExistsError()

        user = self.repo.create_user(
            email=email,
            password_hash=hash_password(password),
            terms_accepted_at=utc_now(),
            terms_version=LEGAL_TERMS_VERSION,
        )
        self.send_verification(user.email)
        return user


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

        if REQUIRE_EMAIL_VERIFICATION and not user.is_email_verified:
            raise EmailNotVerifiedError()

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

    def send_verification(self, email: str) -> None:
        user = self.repo.get_by_email(email)
        if not user or user.is_email_verified:
            return
        token = create_action_token(
            user.id, user.token_version or 0, "verify_email", 24 * 60
        )
        link = f"{FRONTEND_URL}/verify-email?token={token}"
        self.email_service.send(
            user.email,
            "Verify your NextHire AI email",
            f"Verify your email by opening this link:\n\n{link}\n\n"
            "This link expires in 24 hours.",
        )

    def confirm_verification(self, token: str) -> None:
        user = self._user_for_action_token(token, "verify_email")
        user.is_email_verified = True
        self.repo.save(user)

    def send_password_reset(self, email: str) -> None:
        user = self.repo.get_by_email(email)
        if not user:
            return
        token = create_action_token(
            user.id, user.token_version or 0, "reset_password", 30
        )
        link = f"{FRONTEND_URL}/reset-password?token={token}"
        self.email_service.send(
            user.email,
            "Reset your NextHire AI password",
            f"Reset your password by opening this link:\n\n{link}\n\n"
            "This link expires in 30 minutes.",
        )

    def reset_password(self, token: str, new_password: str) -> None:
        user = self._user_for_action_token(token, "reset_password")
        user.password_hash = hash_password(new_password)
        user.token_version = (user.token_version or 0) + 1
        user.failed_login_attempts = 0
        user.locked_until = None
        self.repo.save(user)

    def _user_for_action_token(self, token: str, purpose: str):
        payload = decode_action_token(token, purpose)
        if not payload:
            raise InvalidActionTokenError()
        user = self.repo.get_by_id(payload.get("user_id"))
        if not user or payload.get("token_version") != (user.token_version or 0):
            raise InvalidActionTokenError()
        return user
