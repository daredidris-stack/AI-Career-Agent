import base64
import binascii
import hashlib
import hmac
from datetime import UTC, datetime, time, timedelta
from typing import Any
from urllib.parse import urlencode
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from backend.core.settings import (
    FRONTEND_URL,
    JOB_ALERT_EMAIL_ENABLED,
    JOB_ALERT_MAX_JOBS_PER_EMAIL,
    JOB_ALERT_RETRY_MINUTES,
    JOB_ALERT_SEND_HOUR,
    require_jwt_secret,
)
from backend.core.time import utc_now
from backend.repositories.job_library_repository import JobLibraryRepository
from backend.services.email_service import EmailService
from backend.services.job_library_service import (
    JobLibraryItemNotFoundError,
    JobLibraryService,
)


class InvalidUnsubscribeTokenError(Exception):
    pass


class JobAlertService:
    def __init__(
        self,
        repository: JobLibraryRepository,
        email_service: EmailService | None = None,
        signing_secret: str | None = None,
    ):
        self.repository = repository
        self.email_service = email_service or EmailService()
        self.signing_secret = signing_secret
        self.library = JobLibraryService(repository)

    @property
    def available(self) -> bool:
        return JOB_ALERT_EMAIL_ENABLED and self.email_service.configured

    def status_for_user(self, user) -> dict[str, Any]:
        return {
            "available": self.available,
            "email_delivery_configured": self.email_service.configured,
            "job_alerts_enabled": JOB_ALERT_EMAIL_ENABLED,
            "email_verified": bool(user.is_email_verified),
        }

    def update_preferences(
        self,
        user,
        saved_search_id: int,
        enabled: bool,
        frequency: str,
        timezone_name: str,
    ) -> dict[str, Any]:
        saved_search = self.repository.get_search(
            saved_search_id,
            user.id,
        )
        if not saved_search:
            raise JobLibraryItemNotFoundError()
        normalized_timezone = self.validate_timezone(timezone_name)
        if frequency not in {"daily", "weekly"}:
            raise ValueError("Choose daily or weekly alerts.")
        if enabled and not user.is_email_verified:
            raise ValueError(
                "Verify your account email before enabling email alerts."
            )
        if enabled and not self.available:
            raise ValueError(
                "Automatic email alerts are not configured yet."
            )

        saved_search.email_alerts_enabled = enabled
        saved_search.alert_frequency = frequency
        saved_search.alert_timezone = normalized_timezone
        saved_search.next_alert_at = (
            self.next_delivery_at(frequency, normalized_timezone)
            if enabled
            else None
        )
        saved = self.repository.save_search(saved_search)
        return self.library.search_response(saved)

    def list_deliveries(self, user_id: int) -> list[dict[str, Any]]:
        return [
            {
                "id": delivery.id,
                "saved_search_id": delivery.saved_search_id,
                "status": delivery.status,
                "match_count": delivery.match_count,
                "error_code": delivery.error_code,
                "created_at": delivery.created_at,
                "sent_at": delivery.sent_at,
            }
            for delivery in self.repository.list_deliveries_for_user(user_id)
        ]

    def claim_search(self, saved_search) -> None:
        saved_search.next_alert_at = utc_now() + timedelta(
            minutes=JOB_ALERT_RETRY_MINUTES
        )
        self.repository.save_search(saved_search)

    def complete_search(self, saved_search) -> None:
        saved_search.next_alert_at = self.next_delivery_at(
            saved_search.alert_frequency,
            saved_search.alert_timezone,
        )
        self.repository.save_search(saved_search)

    def send_matches(
        self,
        saved_search,
        user,
        jobs: list[dict[str, Any]],
    ) -> bool:
        if not self.available or not jobs:
            return False
        batch_key = self.batch_key(jobs)
        delivery = self.repository.get_delivery_by_batch(
            saved_search.id,
            batch_key,
        )
        if delivery and delivery.status == "sent":
            return True
        if not delivery:
            delivery = self.repository.create_delivery(
                user_id=user.id,
                saved_search_id=saved_search.id,
                batch_key=batch_key,
                status="pending",
                match_count=len(jobs),
            )
        else:
            delivery.status = "pending"
            delivery.error_code = None
            delivery.match_count = len(jobs)
            delivery = self.repository.save_delivery(delivery)

        unsubscribe_url = self.unsubscribe_url(
            user.id,
            saved_search.id,
        )
        sent = self.email_service.send(
            user.email,
            self.subject(saved_search.name, len(jobs)),
            self.body(saved_search, jobs, unsubscribe_url),
            headers={
                "List-Unsubscribe": f"<{unsubscribe_url}>",
            },
        )
        delivery.status = "sent" if sent else "failed"
        delivery.error_code = None if sent else "smtp_delivery_failed"
        delivery.sent_at = utc_now() if sent else None
        self.repository.save_delivery(delivery)
        if sent:
            saved_search.last_email_at = delivery.sent_at
            self.repository.save_search(saved_search)
        return sent

    def unsubscribe(self, token: str) -> dict[str, Any]:
        user_id, saved_search_id = self.decode_unsubscribe_token(token)
        saved_search = self.repository.get_search(
            saved_search_id,
            user_id,
        )
        if not saved_search:
            raise InvalidUnsubscribeTokenError()
        saved_search.email_alerts_enabled = False
        saved_search.next_alert_at = None
        self.repository.save_search(saved_search)
        return {
            "message": "Email alerts are turned off for this saved search.",
            "saved_search_name": saved_search.name,
        }

    def unsubscribe_url(self, user_id: int, saved_search_id: int) -> str:
        token = self.create_unsubscribe_token(user_id, saved_search_id)
        return (
            f"{FRONTEND_URL.rstrip('/')}/email-preferences?"
            f"{urlencode({'token': token})}"
        )

    def create_unsubscribe_token(
        self,
        user_id: int,
        saved_search_id: int,
    ) -> str:
        payload = f"{user_id}:{saved_search_id}".encode("utf-8")
        signature = hmac.new(
            self._secret().encode("utf-8"),
            payload,
            hashlib.sha256,
        ).digest()
        return ".".join([
            self._encode(payload),
            self._encode(signature),
        ])

    def decode_unsubscribe_token(self, token: str) -> tuple[int, int]:
        try:
            payload_part, signature_part = token.split(".", 1)
            payload = self._decode(payload_part)
            supplied_signature = self._decode(signature_part)
            expected_signature = hmac.new(
                self._secret().encode("utf-8"),
                payload,
                hashlib.sha256,
            ).digest()
            if not hmac.compare_digest(
                supplied_signature,
                expected_signature,
            ):
                raise ValueError()
            user_id, saved_search_id = (
                int(value)
                for value in payload.decode("utf-8").split(":", 1)
            )
            if user_id < 1 or saved_search_id < 1:
                raise ValueError()
            return user_id, saved_search_id
        except (
            binascii.Error,
            TypeError,
            ValueError,
            UnicodeDecodeError,
        ) as error:
            raise InvalidUnsubscribeTokenError() from error

    @staticmethod
    def validate_timezone(timezone_name: str) -> str:
        normalized = timezone_name.strip()
        try:
            ZoneInfo(normalized)
        except (ValueError, ZoneInfoNotFoundError) as error:
            raise ValueError("Choose a valid timezone.") from error
        return normalized

    @staticmethod
    def next_delivery_at(
        frequency: str,
        timezone_name: str,
        now: datetime | None = None,
    ) -> datetime:
        timezone = ZoneInfo(timezone_name)
        current_utc = now or datetime.now(UTC)
        if current_utc.tzinfo is None:
            current_utc = current_utc.replace(tzinfo=UTC)
        local_now = current_utc.astimezone(timezone)
        candidate = datetime.combine(
            local_now.date(),
            time(hour=JOB_ALERT_SEND_HOUR),
            tzinfo=timezone,
        )
        if frequency == "weekly":
            candidate += timedelta(days=(7 - candidate.weekday()) % 7)
            if candidate <= local_now:
                candidate += timedelta(days=7)
        elif candidate <= local_now:
            candidate += timedelta(days=1)
        return candidate.astimezone(UTC).replace(tzinfo=None)

    @classmethod
    def batch_key(cls, jobs: list[dict[str, Any]]) -> str:
        keys = sorted({
            JobLibraryService.job_key(job)
            for job in jobs
        })
        return hashlib.sha256("|".join(keys).encode("utf-8")).hexdigest()

    @staticmethod
    def subject(search_name: str, match_count: int) -> str:
        noun = "job" if match_count == 1 else "jobs"
        return f"{match_count} new {noun} for {search_name} | NextHire AI"

    @staticmethod
    def body(
        saved_search,
        jobs: list[dict[str, Any]],
        unsubscribe_url: str,
    ) -> str:
        shown_jobs = jobs[:JOB_ALERT_MAX_JOBS_PER_EMAIL]
        lines = [
            f"{len(jobs)} new job matches were found for "
            f'"{saved_search.name}".',
            "",
        ]
        for job in shown_jobs:
            provider_url = job.get("listing_url") or job.get("apply_url")
            details = [
                f"{job.get('title') or 'Untitled role'} at "
                f"{job.get('company') or 'Company not listed'}",
                f"Location: {job.get('location') or 'Not listed'}",
                f"Source: {job.get('source') or 'Job provider'}",
            ]
            if provider_url:
                details.append(f"Listing: {provider_url}")
            details.append("")
            lines.extend(details)
        if len(jobs) > len(shown_jobs):
            lines.extend([
                f"{len(jobs) - len(shown_jobs)} additional matches are "
                "available in Job Library.",
                "",
            ])
        lines.extend([
            f"Open Job Library: {FRONTEND_URL.rstrip('/')}/job-library",
            "",
            "You received this because you explicitly enabled email alerts "
            "for this saved search.",
            f"Turn off this alert: {unsubscribe_url}",
        ])
        return "\n".join(lines)

    def _secret(self) -> str:
        return self.signing_secret or require_jwt_secret()

    @staticmethod
    def _encode(value: bytes) -> str:
        return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")

    @staticmethod
    def _decode(value: str) -> bytes:
        padding = "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(value + padding)
