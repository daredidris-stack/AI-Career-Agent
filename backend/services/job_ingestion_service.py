import logging
from datetime import datetime, timedelta
from typing import Callable

from backend.core.settings import (
    JOB_INGESTION_INTERVAL_SECONDS,
    JOB_INGESTION_QUERIES,
    JOB_INGESTION_RESULTS_PER_TARGET,
    JOB_INGESTION_RETRY_SECONDS,
    JOB_LISTING_STALE_DAYS,
)
from backend.core.time import utc_now
from backend.repositories.job_listing_repository import (
    JobListingRepository,
    sync_key,
)
from backend.repositories.profile_repository import ProfileRepository
from fantastic_jobs_api import search_jobs as fantastic_search


logger = logging.getLogger(__name__)
EMPLOYER_INDEX_NAME = "Employer index"
EMPLOYER_INDEX_HOMEPAGE = "https://fantastic.jobs/"
EMPLOYER_INDEX_API_PAGE = (
    "https://developer.fantastic.jobs/documentation/endpoints/new-jobs"
)


class JobIngestionService:
    def __init__(
        self,
        listing_repository: JobListingRepository,
        profile_repository: ProfileRepository,
        provider_search: Callable[..., list[dict]] = fantastic_search,
    ):
        self.listing_repository = listing_repository
        self.profile_repository = profile_repository
        self.provider_search = provider_search

    def run_once(
        self,
        *,
        force: bool = False,
        now: datetime | None = None,
    ) -> dict:
        attempted_at = now or utc_now()
        report = {
            "targets": 0,
            "skipped": 0,
            "failed": 0,
            "fetched": 0,
            "created": 0,
            "updated": 0,
            "deactivated": 0,
        }
        for keyword, location in self.targets():
            report["targets"] += 1
            key = sync_key(EMPLOYER_INDEX_NAME, keyword, location)
            state = self.listing_repository.get_sync_state(key)
            if (
                not force
                and state is not None
                and state.next_sync_at is not None
                and state.next_sync_at > attempted_at
            ):
                report["skipped"] += 1
                continue

            initial_sync = state is None or state.last_success_at is None
            time_frame = "6m" if initial_sync else "24h"
            try:
                jobs = self.provider_search(
                    keyword,
                    location,
                    1,
                    JOB_INGESTION_RESULTS_PER_TARGET,
                    time_frame=time_frame,
                )
                self._annotate_jobs(jobs)
                counts = self.listing_repository.upsert_many(
                    jobs,
                    source=EMPLOYER_INDEX_NAME,
                    seen_at=attempted_at,
                )
                self.listing_repository.record_sync_success(
                    sync_key=key,
                    provider=EMPLOYER_INDEX_NAME,
                    keyword=keyword,
                    location=location,
                    fetched=len(jobs),
                    created=counts["created"],
                    updated=counts["updated"],
                    attempted_at=attempted_at,
                    next_sync_at=(
                        attempted_at
                        + timedelta(seconds=JOB_INGESTION_INTERVAL_SECONDS)
                    ),
                )
                report["fetched"] += len(jobs)
                report["created"] += counts["created"]
                report["updated"] += counts["updated"]
            except Exception as error:
                self.listing_repository.rollback()
                logger.warning(
                    "Job ingestion failed for %s in %s (%s)",
                    keyword,
                    location,
                    type(error).__name__,
                )
                self.listing_repository.record_sync_failure(
                    sync_key=key,
                    provider=EMPLOYER_INDEX_NAME,
                    keyword=keyword,
                    location=location,
                    error_message="Job ingestion failed.",
                    attempted_at=attempted_at,
                    next_sync_at=(
                        attempted_at
                        + timedelta(seconds=JOB_INGESTION_RETRY_SECONDS)
                    ),
                )
                report["failed"] += 1

        report["deactivated"] = (
            self.listing_repository.deactivate_expired(
                now=attempted_at,
                stale_days=JOB_LISTING_STALE_DAYS,
            )
        )
        return report

    def targets(self) -> list[tuple[str, str]]:
        targets = [
            target
            for value in JOB_INGESTION_QUERIES
            if (target := _parse_target(value)) is not None
        ]
        targets.extend(
            self.profile_repository.list_job_search_targets(limit=10)
        )
        unique = []
        seen = set()
        for keyword, location in targets:
            key = (keyword.casefold(), location.casefold())
            if key in seen:
                continue
            unique.append((keyword, location))
            seen.add(key)
        return unique[:10]

    @staticmethod
    def _annotate_jobs(jobs: list[dict]) -> None:
        for job in jobs:
            job["source"] = EMPLOYER_INDEX_NAME
            job["source_homepage"] = EMPLOYER_INDEX_HOMEPAGE
            job["source_api_page"] = EMPLOYER_INDEX_API_PAGE
            job["listing_url"] = (
                job.get("apply_url") or job.get("url") or ""
            )


def _parse_target(value: str) -> tuple[str, str] | None:
    parts = [part.strip() for part in str(value).split("|", 1)]
    keyword = parts[0]
    if not keyword:
        return None
    location = parts[1] if len(parts) == 2 and parts[1] else "Worldwide"
    return keyword, location
