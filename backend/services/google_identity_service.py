from dataclasses import dataclass

from google.auth.exceptions import GoogleAuthError, TransportError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from backend.core.settings import GOOGLE_CLIENT_ID


class GoogleIdentityError(Exception):
    """Raised when Google returns an invalid or unusable identity token."""


class GoogleIdentityUnavailableError(Exception):
    """Raised when Google's signing keys cannot be reached."""


class GoogleIdentityNotConfiguredError(Exception):
    """Raised when the application has no Google OAuth client ID."""


@dataclass(frozen=True)
class GoogleIdentity:
    subject: str
    email: str
    first_name: str = ""
    last_name: str = ""
    hosted_domain: str = ""

    @property
    def email_authoritative(self) -> bool:
        return (
            self.email.endswith("@gmail.com")
            or bool(self.hosted_domain)
        )


class GoogleIdentityService:
    def __init__(self, client_id: str | None = None):
        self.client_id = (
            GOOGLE_CLIENT_ID if client_id is None else client_id
        )

    def verify(self, credential: str) -> GoogleIdentity:
        if not self.client_id:
            raise GoogleIdentityNotConfiguredError()

        try:
            claims = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                self.client_id,
                clock_skew_in_seconds=10,
            )
        except TransportError:
            raise GoogleIdentityUnavailableError() from None
        except (GoogleAuthError, ValueError, TypeError):
            raise GoogleIdentityError() from None

        subject = str(claims.get("sub") or "").strip()
        email = str(claims.get("email") or "").strip().casefold()
        email_verified = claims.get("email_verified")
        if isinstance(email_verified, str):
            email_verified = email_verified.casefold() == "true"

        if not subject or not email or email_verified is not True:
            raise GoogleIdentityError()

        return GoogleIdentity(
            subject=subject,
            email=email,
            first_name=str(claims.get("given_name") or "").strip(),
            last_name=str(claims.get("family_name") or "").strip(),
            hosted_domain=str(claims.get("hd") or "").strip().casefold(),
        )
