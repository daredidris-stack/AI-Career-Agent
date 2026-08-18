from datetime import timedelta
import hashlib
import secrets

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
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from backend.core.time import utc_now

from backend.repositories.user_repository import UserRepository
from backend.repositories.refresh_token_repository import RefreshTokenRepository

from backend.exceptions.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    LoginLockedError,
    EmailNotVerifiedError,
    InvalidActionTokenError,
    GoogleAccountConflictError,
)
from backend.services.email_service import EmailService
from backend.services.google_identity_service import GoogleIdentity


MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15


class AuthService:

    def __init__(
        self,
        repo: UserRepository,
        email_service: EmailService | None = None,
        refresh_token_repo: RefreshTokenRepository | None = None,
    ):
        self.repo = repo
        self.email_service = email_service or EmailService()
        self.refresh_token_repo = refresh_token_repo


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

        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "token_version": user.token_version or 0,
            }
        )
        refresh_token = self._create_refresh_token_for_user(user) if self.refresh_token_repo else None
        return access_token, refresh_token


    def authenticate_google(self, identity: GoogleIdentity):
        user = self.repo.get_by_google_subject(identity.subject)
        needs_save = False
        if not user:
            if not identity.email_authoritative:
                raise GoogleAccountConflictError()

            user = self.repo.get_by_email(identity.email)
            if user and getattr(user, "google_subject", None) not in {
                None,
                identity.subject,
            }:
                raise GoogleAccountConflictError()

            if user:
                user.google_subject = identity.subject
                user.is_email_verified = True
                if not getattr(user, "first_name", None):
                    user.first_name = identity.first_name or None
                if not getattr(user, "last_name", None):
                    user.last_name = identity.last_name or None
                needs_save = True
            else:
                user = self.repo.create_user(
                    email=identity.email,
                    password_hash=hash_password(
                        secrets.token_urlsafe(48)
                    ),
                    terms_accepted_at=utc_now(),
                    terms_version=LEGAL_TERMS_VERSION,
                    google_subject=identity.subject,
                    is_email_verified=True,
                    first_name=identity.first_name or None,
                    last_name=identity.last_name or None,
                )

        if (
            getattr(user, "terms_accepted_at", None) is None
            or getattr(user, "terms_version", None) != LEGAL_TERMS_VERSION
        ):
            user.terms_accepted_at = utc_now()
            user.terms_version = LEGAL_TERMS_VERSION
            needs_save = True

        if user.failed_login_attempts or user.locked_until:
            user.failed_login_attempts = 0
            user.locked_until = None
            needs_save = True

        if needs_save:
            self.repo.save(user)

        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "token_version": user.token_version or 0,
            }
        )
        refresh_token = self._create_refresh_token_for_user(user) if self.refresh_token_repo else None
        return access_token, refresh_token

    def _create_refresh_token_for_user(self, user) -> str:
        """Generate a refresh token, store its hash, and return the plain token."""
        # Generate a random token
        plain_token = secrets.token_urlsafe(64)
        # Hash the token (SHA-256)
        token_hash = hashlib.sha256(plain_token.encode()).hexdigest()
        # Expiration
        expires_at = utc_now() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        # Store
        self.refresh_token_repo.create(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        return plain_token

    def _get_user_id_from_refresh_token(self, token: str) -> int | None:
        """Validate a refresh token and return the user ID if valid."""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        stored = self.refresh_token_repo.get_by_token_hash(token_hash)
        if not stored:
            return None
        if stored.revoked_at is not None:
            return None
        if stored.expires_at < utc_now():
            return None
        return stored.user_id

    def rotate_refresh_token(self, token: str):
        """Validate the refresh token, revoke it, and create a new pair."""
        user_id = self._get_user_id_from_refresh_token(token)
        if not user_id:
            return None, None
        # Revoke the old refresh token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self.refresh_token_repo.revoke(token_hash)
        # Get the user
        user = self.repo.get_by_id(user_id)
        if not user:
            return None, None
        # Create new access and refresh tokens
        access_token = create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
                "token_version": user.token_version or 0,
            }
        )
        refresh_token = self._create_refresh_token_for_user(user)
        return access_token, refresh_token

    def revoke_refresh_token(self, token: str) -> None:
        """Revoke a refresh token (given the plain token)."""
        if not self.refresh_token_repo:
            return
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        self.refresh_token_repo.revoke(token_hash)

    def revoke_all_refresh_tokens_for_user(self, user_id: int) -> None:
        """Revoke all refresh tokens for a user."""
        if not self.refresh_token_repo:
            return
        self.refresh_token_repo.revoke_all_for_user(user_id)

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
