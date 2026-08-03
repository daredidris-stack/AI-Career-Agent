import hashlib
import json
from typing import Any
from urllib.parse import urlparse

from backend.core.time import utc_now
from backend.repositories.job_library_repository import JobLibraryRepository


class JobLibraryItemNotFoundError(Exception):
    pass


class JobLibraryService:
    MAX_SEEN_JOB_KEYS = 1000

    def __init__(self, repository: JobLibraryRepository):
        self.repository = repository

    def list_saved_jobs(self, user_id: int) -> list[dict[str, Any]]:
        return [
            self._saved_job_response(item)
            for item in self.repository.list_saved_jobs(user_id)
        ]

    def save_job(
        self,
        user_id: int,
        values: dict[str, Any],
    ) -> dict[str, Any]:
        cleaned = self._clean_job(values)
        job_key = self.job_key(cleaned)
        existing = self.repository.get_saved_job_by_key(user_id, job_key)
        serialized = json.dumps(cleaned, sort_keys=True)

        if existing:
            existing.title = cleaned["title"]
            existing.company = cleaned["company"]
            existing.source = cleaned.get("source")
            existing.source_job_id = cleaned.get("source_job_id")
            existing.location = cleaned.get("location")
            existing.listing_url = cleaned.get("listing_url")
            existing.apply_url = cleaned.get("apply_url")
            existing.job_data_json = serialized
            return self._saved_job_response(
                self.repository.save_saved_job(existing)
            )

        saved_job = self.repository.create_saved_job(
            user_id=user_id,
            job_key=job_key,
            title=cleaned["title"],
            company=cleaned["company"],
            source=cleaned.get("source"),
            source_job_id=cleaned.get("source_job_id"),
            location=cleaned.get("location"),
            listing_url=cleaned.get("listing_url"),
            apply_url=cleaned.get("apply_url"),
            job_data_json=serialized,
        )
        return self._saved_job_response(saved_job)

    def delete_saved_job(self, user_id: int, saved_job_id: int) -> None:
        saved_job = self.repository.get_saved_job(saved_job_id, user_id)
        if not saved_job:
            raise JobLibraryItemNotFoundError()
        self.repository.delete_saved_job(saved_job)

    def list_searches(self, user_id: int) -> list[dict[str, Any]]:
        return [
            self.search_response(item)
            for item in self.repository.list_searches(user_id)
        ]

    def create_search(
        self,
        user_id: int,
        name: str,
        filters: dict[str, Any],
    ) -> dict[str, Any]:
        normalized_name = name.strip()
        normalized_filters = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in filters.items()
        }
        saved_search = self.repository.create_search(
            user_id=user_id,
            name=normalized_name,
            filters_json=json.dumps(normalized_filters, sort_keys=True),
        )
        return self.search_response(saved_search)

    def get_search(self, user_id: int, saved_search_id: int):
        saved_search = self.repository.get_search(saved_search_id, user_id)
        if not saved_search:
            raise JobLibraryItemNotFoundError()
        return saved_search

    def search_filters(self, saved_search) -> dict[str, Any]:
        return self._json_object(saved_search.filters_json)

    def delete_search(self, user_id: int, saved_search_id: int) -> None:
        self.repository.delete_search(
            self.get_search(user_id, saved_search_id)
        )

    def acknowledge_search(
        self,
        user_id: int,
        saved_search_id: int,
    ) -> dict[str, Any]:
        saved_search = self.get_search(user_id, saved_search_id)
        saved_search.new_match_count = 0
        return self.search_response(
            self.repository.save_search(saved_search)
        )

    def record_search_results(
        self,
        saved_search,
        jobs: list[dict[str, Any]],
    ) -> dict[str, Any]:
        previous_keys = set(self._json_list(saved_search.seen_job_keys_json))
        current_keys = [self.job_key(job) for job in jobs]
        new_keys = {self.job_key(job) for job in self.new_jobs(
            saved_search,
            jobs,
        )}
        combined_keys = list(dict.fromkeys(current_keys + list(previous_keys)))
        saved_search.seen_job_keys_json = json.dumps(
            combined_keys[: self.MAX_SEEN_JOB_KEYS]
        )
        saved_search.new_match_count = len(new_keys)
        saved_search.last_result_count = len(jobs)
        saved_search.last_run_at = utc_now()
        return self.search_response(
            self.repository.save_search(saved_search)
        )

    def search_response(self, item) -> dict[str, Any]:
        return self._saved_search_response(item)

    def new_jobs(
        self,
        saved_search,
        jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        if not saved_search.last_run_at:
            return []
        previous_keys = set(
            self._json_list(saved_search.seen_job_keys_json)
        )
        return [
            job
            for job in jobs
            if self.job_key(job) not in previous_keys
        ]

    @classmethod
    def job_key(cls, job: dict[str, Any]) -> str:
        source = str(job.get("source") or "").strip().casefold()
        source_job_id = str(job.get("source_job_id") or "").strip()
        if source_job_id:
            identity = f"source:{source}:{source_job_id}"
        else:
            url = cls._safe_url(
                job.get("apply_url") or job.get("listing_url"),
                required=False,
            )
            identity = (
                f"url:{url}"
                if url
                else "job:{title}|{company}|{location}".format(
                    title=str(job.get("title") or "").strip().casefold(),
                    company=str(job.get("company") or "").strip().casefold(),
                    location=str(job.get("location") or "").strip().casefold(),
                )
            )
        return hashlib.sha256(identity.encode("utf-8")).hexdigest()

    @classmethod
    def _clean_job(cls, values: dict[str, Any]) -> dict[str, Any]:
        cleaned = {
            key: value.strip() if isinstance(value, str) else value
            for key, value in values.items()
        }
        if not cleaned.get("title") or not cleaned.get("company"):
            raise ValueError("Job title and company are required.")
        cleaned["listing_url"] = cls._safe_url(
            cleaned.get("listing_url"),
            required=False,
        )
        cleaned["apply_url"] = cls._safe_url(
            cleaned.get("apply_url"),
            required=False,
        )
        if not cleaned["listing_url"] and not cleaned["apply_url"]:
            raise ValueError("A secure provider job URL is required.")
        return cleaned

    @staticmethod
    def _safe_url(value: Any, required: bool) -> str | None:
        candidate = str(value or "").strip()
        if not candidate and not required:
            return None
        parsed = urlparse(candidate)
        if (
            parsed.scheme != "https"
            or not parsed.hostname
            or parsed.username
            or parsed.password
        ):
            raise ValueError("A secure provider job URL is required.")
        return candidate

    @staticmethod
    def _json_object(value: str) -> dict[str, Any]:
        try:
            parsed = json.loads(value or "{}")
        except (TypeError, json.JSONDecodeError):
            return {}
        return parsed if isinstance(parsed, dict) else {}

    @staticmethod
    def _json_list(value: str) -> list[str]:
        try:
            parsed = json.loads(value or "[]")
        except (TypeError, json.JSONDecodeError):
            return []
        return [str(item) for item in parsed] if isinstance(parsed, list) else []

    @classmethod
    def _saved_job_response(cls, item) -> dict[str, Any]:
        return {
            "id": item.id,
            "job_key": item.job_key,
            "job": cls._json_object(item.job_data_json),
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }

    @classmethod
    def _saved_search_response(cls, item) -> dict[str, Any]:
        return {
            "id": item.id,
            "name": item.name,
            "filters": cls._json_object(item.filters_json),
            "new_match_count": item.new_match_count,
            "last_result_count": item.last_result_count,
            "last_run_at": item.last_run_at,
            "email_alerts_enabled": bool(
                getattr(item, "email_alerts_enabled", False)
            ),
            "alert_frequency": (
                getattr(item, "alert_frequency", "daily") or "daily"
            ),
            "alert_timezone": (
                getattr(item, "alert_timezone", "UTC") or "UTC"
            ),
            "next_alert_at": getattr(item, "next_alert_at", None),
            "last_email_at": getattr(item, "last_email_at", None),
            "created_at": item.created_at,
            "updated_at": item.updated_at,
        }
