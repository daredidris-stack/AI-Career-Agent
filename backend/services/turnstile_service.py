from collections.abc import Collection
from typing import Any

import requests

from backend.core.settings import (
    APP_ENV,
    TURNSTILE_ALLOWED_HOSTNAMES,
    TURNSTILE_SECRET_KEY,
)


SITEVERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
TEST_SECRET_KEYS = {
    "1x0000000000000000000000000000000AA",
    "2x0000000000000000000000000000000AA",
    "3x0000000000000000000000000000000AA",
}


class TurnstileVerificationError(Exception):
    """Raised when Cloudflare rejects or cannot validate a challenge token."""


class TurnstileUnavailableError(Exception):
    """Raised when Cloudflare's validation service cannot be reached."""


class TurnstileService:
    def __init__(
        self,
        secret_key: str | None = TURNSTILE_SECRET_KEY,
        allowed_hostnames: Collection[str] = TURNSTILE_ALLOWED_HOSTNAMES,
        allow_test_keys: bool = APP_ENV != "production",
    ):
        self.secret_key = (secret_key or "").strip()
        self.allow_test_keys = allow_test_keys
        self.allowed_hostnames = {
            hostname.strip().casefold()
            for hostname in allowed_hostnames
            if hostname.strip()
        }

    @property
    def enabled(self) -> bool:
        return bool(self.secret_key)

    def verify(self, token: str | None, expected_action: str) -> None:
        if not self.enabled:
            return
        if (
            self.secret_key in TEST_SECRET_KEYS
            and not self.allow_test_keys
        ):
            raise TurnstileVerificationError()
        if not token or not token.strip():
            raise TurnstileVerificationError()

        try:
            response = requests.post(
                SITEVERIFY_URL,
                data={
                    "secret": self.secret_key,
                    "response": token.strip(),
                },
                timeout=10,
            )
            response.raise_for_status()
            result: Any = response.json()
        except (requests.RequestException, ValueError):
            raise TurnstileUnavailableError() from None

        if not isinstance(result, dict):
            raise TurnstileUnavailableError()
        if not result.get("success"):
            raise TurnstileVerificationError()

        if result.get("action") != expected_action:
            raise TurnstileVerificationError()

        hostname = str(result.get("hostname") or "").casefold()
        if (
            not self.allowed_hostnames
            or hostname not in self.allowed_hostnames
        ):
            raise TurnstileVerificationError()
