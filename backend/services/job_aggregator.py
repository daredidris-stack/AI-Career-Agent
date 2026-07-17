import logging

from job_search import search_jobs as remoteok_search
from adzuna_api import search_jobs as adzuna_search
from arbeitnow_api import search_jobs as arbeitnow_search


logger = logging.getLogger(__name__)


def aggregate_jobs(
    keyword,
    location="Remote",
    industry="",
):

    jobs = []


    # RemoteOK jobs
    try:
        remote_jobs = remoteok_search(keyword)

        for job in remote_jobs:
            job["source"] = "RemoteOK"

        jobs.extend(remote_jobs)

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

        jobs.extend(arbeitnow_jobs)
    except Exception:
        logger.exception("Arbeitnow job search failed")



    # Adzuna jobs
    try:
        adzuna_jobs = adzuna_search(
            " ".join(
                value
                for value in (keyword, industry)
                if value
            ),
            location
        )

        for job in adzuna_jobs:
            job["source"] = "Adzuna"

        jobs.extend(adzuna_jobs)

    except Exception:
        logger.exception("Adzuna job search failed")



    unique_jobs = []
    seen = set()

    for job in jobs:
        key = (
            str(job.get("title") or "").casefold(),
            str(job.get("company") or "").casefold(),
        )
        if key not in seen:
            unique_jobs.append(job)
            seen.add(key)

    return unique_jobs[:5]
