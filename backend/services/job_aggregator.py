import logging

from job_search import search_jobs as remoteok_search
from adzuna_api import search_jobs as adzuna_search
from arbeitnow_api import search_jobs as arbeitnow_search
from himalayas_api import search_jobs as himalayas_search
from jooble_api import search_jobs as jooble_search


logger = logging.getLogger(__name__)


def aggregate_jobs(
    keyword,
    location="Remote",
    industry="",
    page=1,
    results=20,
):
    provider_batches = []
    search_term = " ".join(
        value for value in (keyword, industry) if value
    )

    try:
        jooble_jobs = jooble_search(
            search_term,
            location,
            page,
            results,
        )

        for job in jooble_jobs:
            job["source"] = "Jooble"

        provider_batches.append(jooble_jobs)
    except Exception:
        logger.exception("Jooble job search failed")

    try:
        himalayas_jobs = himalayas_search(
            search_term,
            location,
            page,
        )

        for job in himalayas_jobs:
            job["source"] = "Himalayas"

        provider_batches.append(himalayas_jobs)
    except Exception:
        logger.exception("Himalayas job search failed")

    # Free feeds supplement the first result page.
    if page == 1:
        try:
            remote_jobs = remoteok_search(keyword)

            for job in remote_jobs:
                job["source"] = "RemoteOK"

            provider_batches.append(remote_jobs)

        except Exception:
            logger.exception("RemoteOK job search failed")

        try:
            arbeitnow_jobs = arbeitnow_search(
                keyword,
                location,
                industry,
            )

            for job in arbeitnow_jobs:
                job["source"] = "Arbeitnow"

            provider_batches.append(arbeitnow_jobs)
        except Exception:
            logger.exception("Arbeitnow job search failed")



        # Adzuna jobs
        try:
            adzuna_jobs = adzuna_search(search_term, location)

            for job in adzuna_jobs:
                job["source"] = "Adzuna"

            provider_batches.append(adzuna_jobs)

        except Exception:
            logger.exception("Adzuna job search failed")

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

    return unique_jobs[:results]
