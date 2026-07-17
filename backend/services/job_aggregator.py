import logging
from collections.abc import Callable
from typing import Any

from job_search import search_jobs as remoteok_search
from adzuna_api import search_jobs as adzuna_search
from arbeitnow_api import search_jobs as arbeitnow_search
from himalayas_api import search_jobs as himalayas_search
from jooble_api import search_jobs as jooble_search
from backend.core.settings import (
    ADZUNA_APP_ID,
    ADZUNA_APP_KEY,
    JOOBLE_API_KEY,
)


logger = logging.getLogger(__name__)

PROVIDER_DISCLOSURES = {
    "Jooble": {
        "homepage": "https://jooble.org/",
        "api_page": "https://jooble.org/api/about",
    },
    "Himalayas": {
        "homepage": "https://himalayas.app/",
        "api_page": "https://himalayas.app/jobs/api",
    },
    "RemoteOK": {
        "homepage": "https://remoteok.com/",
        "api_page": "https://remoteok.com/api",
    },
    "Arbeitnow": {
        "homepage": "https://www.arbeitnow.com/",
        "api_page": "https://www.arbeitnow.com/job-board-api",
    },
    "Adzuna": {
        "homepage": "https://www.adzuna.com/",
        "api_page": "https://developer.adzuna.com/",
    },
}


class AggregatedJobs(list):
    def __init__(self, jobs, provider_status):
        super().__init__(jobs)
        self.provider_status = provider_status


def aggregate_jobs(
    keyword,
    location="Remote",
    industry="",
    page=1,
    results=20,
):
    provider_batches = []
    provider_status = []
    search_term = " ".join(
        value for value in (keyword, industry) if value
    )

    def collect(
        name: str,
        search: Callable[[], list[dict[str, Any]]],
        configured: bool = True,
    ) -> None:
        try:
            jobs = search()
            disclosure = PROVIDER_DISCLOSURES[name]
            for job in jobs:
                job["source"] = name
                job["source_homepage"] = disclosure["homepage"]
                job["source_api_page"] = disclosure["api_page"]
            provider_batches.append(jobs)
            provider_status.append({
                "name": name,
                "status": (
                    "active" if jobs else
                    "no_results" if configured else
                    "not_configured"
                ),
                "count": len(jobs),
                **disclosure,
            })
        except Exception:
            logger.exception("%s job search failed", name)
            provider_status.append({
                "name": name,
                "status": "unavailable",
                "count": 0,
                **PROVIDER_DISCLOSURES[name],
            })

    collect(
        "Jooble",
        lambda: jooble_search(
            search_term,
            location,
            page,
            results,
        ),
        configured=bool(JOOBLE_API_KEY),
    )
    collect(
        "Himalayas",
        lambda: himalayas_search(
            search_term,
            location,
            page,
        ),
    )

    # Free feeds supplement the first result page.
    if page == 1:
        collect("RemoteOK", lambda: remoteok_search(keyword))
        collect(
            "Arbeitnow",
            lambda: arbeitnow_search(
                keyword,
                location,
                industry,
            ),
        )
        collect(
            "Adzuna",
            lambda: adzuna_search(search_term, location),
            configured=bool(ADZUNA_APP_ID and ADZUNA_APP_KEY),
        )

    unique_jobs = []
    seen = set()

    # Blend providers so one large feed cannot hide every other source.
    for index in range(max(map(len, provider_batches), default=0)):
        for batch in provider_batches:
            if index >= len(batch):
                continue
            job = batch[index]
            key = (
                str(job.get("title") or "").casefold(),
                str(job.get("company") or "").casefold(),
            )
            if key not in seen:
                unique_jobs.append(job)
                seen.add(key)

    return AggregatedJobs(unique_jobs[:results], provider_status)
