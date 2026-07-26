import logging
from concurrent.futures import ThreadPoolExecutor
from typing import Any
from urllib.parse import urlparse

from job_search import search_jobs as remoteok_search
from adzuna_api import search_jobs as adzuna_search
from arbeitnow_api import search_jobs as arbeitnow_search
from ats_job_apis import (
    search_ashby_jobs as ashby_search,
    search_greenhouse_jobs as greenhouse_search,
    search_lever_jobs as lever_search,
)
from employer_job_apis import (
    search_apple_jobs as apple_search,
    search_crossover_jobs as crossover_search,
    search_microsoft_jobs as microsoft_search,
)
from fantastic_jobs_api import search_jobs as fantastic_search
from himalayas_api import search_jobs as himalayas_search
from jooble_api import search_jobs as jooble_search
from serpapi_jobs import search_jobs as serpapi_search
from theirstack_api import search_jobs as theirstack_search
from usajobs_api import search_jobs as usajobs_search
from backend.core.settings import (
    ADZUNA_APP_ID,
    ADZUNA_APP_KEY,
    ASHBY_JOB_BOARDS,
    DIRECT_EMPLOYER_JOB_SOURCES,
    FANTASTIC_JOBS_API_KEY,
    GREENHOUSE_JOB_BOARDS,
    JOOBLE_API_KEY,
    LEVER_JOB_SITES,
    SERPAPI_API_KEY,
    THEIRSTACK_API_KEY,
    USAJOBS_API_KEY,
    USAJOBS_USER_AGENT,
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
    "Microsoft": {
        "homepage": "https://careers.microsoft.com/",
        "api_page": "https://careers.microsoft.com/",
    },
    "Apple": {
        "homepage": "https://jobs.apple.com/",
        "api_page": "https://jobs.apple.com/",
    },
    "Crossover": {
        "homepage": "https://www.crossover.com/jobs",
        "api_page": "https://www.crossover.com/jobs",
    },
    "Worldwide index": {
        "homepage": "https://theirstack.com/",
        "api_page": "https://theirstack.com/en/docs/api-reference",
    },
    "Greenhouse employers": {
        "homepage": "https://www.greenhouse.com/",
        "api_page": "https://developers.greenhouse.io/job-board.html",
    },
    "Lever employers": {
        "homepage": "https://www.lever.co/",
        "api_page": "https://github.com/lever/postings-api",
    },
    "Ashby employers": {
        "homepage": "https://www.ashbyhq.com/",
        "api_page": "https://developers.ashbyhq.com/docs/public-job-posting-api",
    },
    "USAJOBS": {
        "homepage": "https://www.usajobs.gov/",
        "api_page": "https://developer.usajobs.gov/api-reference/get-api-search",
    },
    "Google Jobs index": {
        "homepage": "https://www.google.com/search?q=jobs",
        "api_page": "https://serpapi.com/google-jobs-api",
    },
    "Employer index": {
        "homepage": "https://fantastic.jobs/",
        "api_page": (
            "https://developer.fantastic.jobs/documentation/"
            "endpoints/new-jobs"
        ),
    },
}


class AggregatedJobs(list):
    def __init__(self, jobs, provider_status):
        super().__init__(jobs)
        self.provider_status = provider_status


def aggregate_jobs(
    keyword,
    location="Worldwide",
    industry="",
    page=1,
    results=50,
):
    provider_batches = []
    provider_status = []
    search_term = " ".join(
        value for value in (keyword, industry) if value
    )

    def fetch(spec):
        name, search, configured = spec
        disclosure = PROVIDER_DISCLOSURES[name]
        if not configured:
            return [], {
                "name": name,
                "status": "not_configured",
                "count": 0,
                **disclosure,
            }
        try:
            jobs = search()
            for job in jobs:
                job["source"] = name
                job["source_homepage"] = disclosure["homepage"]
                job["source_api_page"] = disclosure["api_page"]
                job["listing_url"] = _listing_url(job)
            return jobs, {
                "name": name,
                "status": (
                    "active" if jobs else
                    "no_results" if configured else
                    "not_configured"
                ),
                "count": len(jobs),
                **disclosure,
            }
        except Exception:
            logger.warning("%s job search failed", name)
            return [], {
                "name": name,
                "status": "unavailable",
                "count": 0,
                **PROVIDER_DISCLOSURES[name],
            }

    provider_specs = [(
        "Jooble",
        lambda: jooble_search(
            search_term,
            location,
            page,
            results,
        ),
        bool(JOOBLE_API_KEY),
    ), (
        "Himalayas",
        lambda: himalayas_search(
            search_term,
            location,
            page,
        ),
        True,
    ), (
        "Microsoft",
        lambda: microsoft_search(keyword, location, page, results),
        "microsoft" in DIRECT_EMPLOYER_JOB_SOURCES,
    ), (
        "Apple",
        lambda: apple_search(keyword, location, page, results),
        "apple" in DIRECT_EMPLOYER_JOB_SOURCES,
    ), (
        "Crossover",
        lambda: crossover_search(keyword, location, page, results),
        "crossover" in DIRECT_EMPLOYER_JOB_SOURCES,
    ), (
        "Employer index",
        lambda: fantastic_search(keyword, location, page, results),
        bool(FANTASTIC_JOBS_API_KEY),
    ), (
        "Worldwide index",
        lambda: theirstack_search(keyword, location, page, results),
        bool(THEIRSTACK_API_KEY),
    ), (
        "Greenhouse employers",
        lambda: greenhouse_search(keyword, location, page, results),
        bool(GREENHOUSE_JOB_BOARDS),
    ), (
        "Lever employers",
        lambda: lever_search(keyword, location, page, results),
        bool(LEVER_JOB_SITES),
    ), (
        "Ashby employers",
        lambda: ashby_search(keyword, location, page, results),
        bool(ASHBY_JOB_BOARDS),
    ), (
        "USAJOBS",
        lambda: usajobs_search(search_term, location, page, results),
        bool(USAJOBS_API_KEY and USAJOBS_USER_AGENT),
    ), (
        "Google Jobs index",
        lambda: serpapi_search(search_term, location, page, results),
        bool(SERPAPI_API_KEY),
    )]

    # Free feeds supplement the first result page.
    if page == 1:
        provider_specs.append(("RemoteOK", lambda: remoteok_search(keyword), True))
        provider_specs.append((
            "Arbeitnow",
            lambda: arbeitnow_search(
                keyword,
                location,
                industry,
                results,
            ),
            True,
        ))
        provider_specs.append((
            "Adzuna",
            lambda: adzuna_search(search_term, location, results),
            bool(ADZUNA_APP_ID and ADZUNA_APP_KEY),
        ))

    with ThreadPoolExecutor(max_workers=len(provider_specs)) as executor:
        for jobs, status in executor.map(fetch, provider_specs):
            provider_batches.append(jobs)
            provider_status.append(status)

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
                str(job.get("location") or "").casefold(),
            )
            if key not in seen:
                unique_jobs.append(job)
                seen.add(key)

    return AggregatedJobs(unique_jobs[:results], provider_status)


def _listing_url(job: dict[str, Any]) -> str:
    """Return only a direct, browser-safe listing URL from a provider result."""
    value = str(
        job.get("apply_url")
        or job.get("redirect_url")
        or job.get("url")
        or ""
    ).strip()
    if not value:
        return ""

    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    return value
