import hashlib
import json
import re
import unicodedata
from datetime import UTC, datetime, timedelta
from typing import Any
from urllib.parse import urlparse

from sqlalchemy import or_
from sqlalchemy.orm import Session

from backend.core.settings import JOB_LISTING_STALE_DAYS
from backend.core.time import utc_now
from backend.models.job_listing import JobListing, JobSyncState


class JobListingRepository:
    def __init__(self, db: Session):
        self.db = db

    def search(
        self,
        keyword: str,
        location: str = "Worldwide",
        page: int = 1,
        per_page: int = 50,
        *,
        now: datetime | None = None,
        stale_days: int = JOB_LISTING_STALE_DAYS,
    ) -> list[dict[str, Any]]:
        timestamp = now or utc_now()
        stale_before = timestamp - timedelta(days=max(1, stale_days))
        terms = _search_terms(keyword)
        if not terms:
            return []
        query = self.db.query(JobListing).filter(
            JobListing.is_active.is_(True),
            or_(
                JobListing.expires_at.is_(None),
                JobListing.expires_at >= timestamp,
            ),
            JobListing.last_seen_at >= stale_before,
        )
        for term in terms:
            pattern = f"%{term}%"
            query = query.filter(or_(
                JobListing.title.ilike(pattern),
                JobListing.description.ilike(pattern),
                JobListing.company.ilike(pattern),
            ))

        location_key = str(location or "").strip().casefold()
        if location_key == "remote":
            query = query.filter(or_(
                JobListing.workplace_type.ilike("%remote%"),
                JobListing.location.ilike("%remote%"),
            ))
        elif location_key not in {"", "worldwide"}:
            for part in (
                value.strip()
                for value in location_key.split(",")
                if value.strip()
            ):
                query = query.filter(JobListing.location.ilike(f"%{part}%"))

        page_size = max(1, min(100, per_page))
        offset = (max(1, page) - 1) * page_size
        listings = (
            query.order_by(
                JobListing.published_at.desc().nullslast(),
                JobListing.last_seen_at.desc(),
            )
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return [self.to_job(listing) for listing in listings]

    def upsert_many(
        self,
        jobs: list[dict[str, Any]],
        source: str | None = None,
        seen_at: datetime | None = None,
    ) -> dict[str, int]:
        timestamp = seen_at or utc_now()
        normalized = []
        for job in jobs:
            values = self._listing_values(job, source, timestamp)
            if values is not None:
                normalized.append(values)
        if not normalized:
            return {"created": 0, "updated": 0, "skipped": len(jobs)}

        keys = [values["dedupe_key"] for values in normalized]
        existing_by_key = {
            listing.dedupe_key: listing
            for listing in self.db.query(JobListing).filter(
                JobListing.dedupe_key.in_(keys)
            )
        }
        created = 0
        updated = 0
        for values in normalized:
            listing = existing_by_key.get(values["dedupe_key"])
            if listing is None:
                listing = JobListing(**values)
                self.db.add(listing)
                existing_by_key[values["dedupe_key"]] = listing
                created += 1
                continue

            self._merge_listing(listing, values)
            updated += 1

        self.db.commit()
        return {
            "created": created,
            "updated": updated,
            "skipped": len(jobs) - len(normalized),
        }

    def deactivate_expired(
        self,
        now: datetime | None = None,
        stale_days: int = 45,
    ) -> int:
        timestamp = now or utc_now()
        stale_before = timestamp - timedelta(days=max(1, stale_days))
        changed = (
            self.db.query(JobListing)
            .filter(
                JobListing.is_active.is_(True),
                or_(
                    JobListing.expires_at < timestamp,
                    JobListing.last_seen_at < stale_before,
                ),
            )
            .update(
                {
                    JobListing.is_active: False,
                    JobListing.updated_at: timestamp,
                },
                synchronize_session=False,
            )
        )
        self.db.commit()
        return changed

    def get_sync_state(self, sync_key: str) -> JobSyncState | None:
        return self.db.query(JobSyncState).filter(
            JobSyncState.sync_key == sync_key
        ).first()

    def rollback(self) -> None:
        self.db.rollback()

    def sync_is_due(self, sync_key: str, now: datetime | None = None) -> bool:
        state = self.get_sync_state(sync_key)
        if state is None or state.next_sync_at is None:
            return True
        return state.next_sync_at <= (now or utc_now())

    def record_sync_success(
        self,
        *,
        sync_key: str,
        provider: str,
        keyword: str,
        location: str,
        fetched: int,
        created: int,
        updated: int,
        attempted_at: datetime,
        next_sync_at: datetime,
    ) -> JobSyncState:
        state = self._sync_state(sync_key, provider, keyword, location)
        state.status = "success"
        state.last_attempt_at = attempted_at
        state.last_success_at = attempted_at
        state.next_sync_at = next_sync_at
        state.jobs_fetched = fetched
        state.jobs_created = created
        state.jobs_updated = updated
        state.error_message = None
        state.updated_at = attempted_at
        self.db.commit()
        self.db.refresh(state)
        return state

    def record_sync_failure(
        self,
        *,
        sync_key: str,
        provider: str,
        keyword: str,
        location: str,
        error_message: str,
        attempted_at: datetime,
        next_sync_at: datetime,
    ) -> JobSyncState:
        state = self._sync_state(sync_key, provider, keyword, location)
        state.status = "failed"
        state.last_attempt_at = attempted_at
        state.next_sync_at = next_sync_at
        state.jobs_fetched = 0
        state.jobs_created = 0
        state.jobs_updated = 0
        state.error_message = error_message[:1000]
        state.updated_at = attempted_at
        self.db.commit()
        self.db.refresh(state)
        return state

    @staticmethod
    def to_job(listing: JobListing) -> dict[str, Any]:
        metadata = _json_object(listing.source_metadata_json)
        return {
            "source_job_id": listing.source_job_id or "",
            "source": listing.source,
            "source_homepage": metadata.get("source_homepage", ""),
            "source_api_page": metadata.get("source_api_page", ""),
            "title": listing.title,
            "company": listing.company,
            "location": listing.location or "",
            "description": listing.description or "",
            "skills": _json_list(listing.skills_json),
            "url": listing.apply_url or listing.listing_url or "",
            "apply_url": listing.apply_url or listing.listing_url or "",
            "listing_url": listing.listing_url or listing.apply_url or "",
            "job_type": listing.job_type or "",
            "workplace_type": listing.workplace_type or "",
            "salary": listing.salary or "",
            "salary_min": listing.salary_min,
            "salary_max": listing.salary_max,
            "salary_currency": listing.salary_currency or "",
            "visa_sponsorship": listing.visa_sponsorship,
            "updated": _isoformat(listing.published_at),
            "expires_at": _isoformat(listing.expires_at),
            "cached": True,
        }

    def _sync_state(
        self,
        sync_key: str,
        provider: str,
        keyword: str,
        location: str,
    ) -> JobSyncState:
        state = self.get_sync_state(sync_key)
        if state is not None:
            return state
        state = JobSyncState(
            sync_key=sync_key,
            provider=provider,
            keyword=keyword,
            location=location,
        )
        self.db.add(state)
        return state

    @staticmethod
    def _listing_values(
        job: dict[str, Any],
        source: str | None,
        timestamp: datetime,
    ) -> dict[str, Any] | None:
        title = str(job.get("title") or "").strip()
        company = str(job.get("company") or "Unknown").strip()
        location = str(job.get("location") or "").strip()
        apply_url = _first_safe_http_url(job.get("apply_url"))
        listing_url = _first_safe_http_url(
            job.get("listing_url"),
            job.get("url"),
            apply_url,
        )
        apply_url = apply_url or listing_url
        if not title or not (apply_url or listing_url):
            return None

        metadata = {
            "source_homepage": _first_safe_http_url(
                job.get("source_homepage")
            ),
            "source_api_page": _first_safe_http_url(
                job.get("source_api_page")
            ),
        }
        return {
            "dedupe_key": job_dedupe_key(title, company, location, listing_url),
            "source": str(source or job.get("source") or "Unknown"),
            "source_job_id": str(job.get("source_job_id") or "") or None,
            "title": title,
            "company": company,
            "location": location or None,
            "description": str(job.get("description") or "").strip() or None,
            "listing_url": listing_url or None,
            "apply_url": apply_url or listing_url or None,
            "job_type": str(job.get("job_type") or "").strip() or None,
            "workplace_type": str(
                job.get("workplace_type") or ""
            ).strip() or None,
            "skills_json": json.dumps(job.get("skills") or []),
            "salary": str(job.get("salary") or "").strip() or None,
            "salary_min": _number(job.get("salary_min")),
            "salary_max": _number(job.get("salary_max")),
            "salary_currency": str(
                job.get("salary_currency") or ""
            ).strip() or None,
            "visa_sponsorship": _boolean_or_none(job.get("visa_sponsorship")),
            "published_at": _datetime_or_none(job.get("updated")),
            "expires_at": _datetime_or_none(job.get("expires_at")),
            "source_metadata_json": json.dumps(metadata),
            "is_active": True,
            "first_seen_at": timestamp,
            "last_seen_at": timestamp,
            "updated_at": timestamp,
        }

    @staticmethod
    def _merge_listing(
        listing: JobListing,
        values: dict[str, Any],
    ) -> None:
        current_description = listing.description or ""
        incoming_description = values.get("description") or ""
        for field in (
            "source",
            "source_job_id",
            "title",
            "company",
            "location",
            "listing_url",
            "apply_url",
            "job_type",
            "workplace_type",
            "skills_json",
            "salary",
            "salary_min",
            "salary_max",
            "salary_currency",
            "visa_sponsorship",
            "published_at",
            "expires_at",
            "source_metadata_json",
        ):
            value = values.get(field)
            if value not in {None, "", "[]", "{}"}:
                setattr(listing, field, value)
        if len(incoming_description) >= len(current_description):
            listing.description = incoming_description or current_description
        listing.is_active = True
        listing.last_seen_at = values["last_seen_at"]
        listing.updated_at = values["updated_at"]


def job_dedupe_key(
    title: str,
    company: str,
    location: str,
    listing_url: str = "",
) -> str:
    identity = "|".join((
        _identity_text(title),
        _identity_text(company),
        _identity_text(location) or _identity_text(listing_url),
    ))
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def sync_key(provider: str, keyword: str, location: str) -> str:
    identity = "|".join((
        _identity_text(provider),
        _identity_text(keyword),
        _identity_text(location),
    ))
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def _identity_text(value: Any) -> str:
    text = unicodedata.normalize("NFKC", str(value or "")).casefold()
    return re.sub(r"[^\w]+", " ", text).strip()


def _search_terms(value: Any) -> list[str]:
    return [term for term in _identity_text(value).split() if len(term) > 1]


def _datetime_or_none(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return _naive_utc(value)
    if isinstance(value, (int, float)):
        timestamp = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(timestamp, UTC).replace(tzinfo=None)
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return _naive_utc(
            datetime.fromisoformat(text.replace("Z", "+00:00"))
        )
    except ValueError:
        return None


def _isoformat(value: datetime | None) -> str:
    return f"{value.isoformat()}Z" if value else ""


def _naive_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value
    return value.astimezone(UTC).replace(tzinfo=None)


def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _boolean_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _first_safe_http_url(*values: Any) -> str:
    for value in values:
        candidate = str(value or "").strip()
        if not candidate:
            continue
        parsed = urlparse(candidate)
        try:
            port = parsed.port
        except ValueError:
            continue
        if (
            parsed.scheme in {"http", "https"}
            and parsed.hostname
            and parsed.username is None
            and parsed.password is None
            and (
                port is None
                or (parsed.scheme == "http" and port == 80)
                or (parsed.scheme == "https" and port == 443)
            )
        ):
            return candidate
    return ""


def _json_list(value: str) -> list[Any]:
    try:
        parsed = json.loads(value or "[]")
    except (TypeError, ValueError):
        return []
    return parsed if isinstance(parsed, list) else []


def _json_object(value: str) -> dict[str, Any]:
    try:
        parsed = json.loads(value or "{}")
    except (TypeError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}
