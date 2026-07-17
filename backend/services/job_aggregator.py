import logging

from job_search import search_jobs as remoteok_search
from adzuna_api import search_jobs as adzuna_search


logger = logging.getLogger(__name__)


def aggregate_jobs(
    keyword,
    location="Remote"
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



    # Adzuna jobs
    try:
        adzuna_jobs = adzuna_search(
            keyword,
            location
        )

        for job in adzuna_jobs:
            job["source"] = "Adzuna"

        jobs.extend(adzuna_jobs)

    except Exception:
        logger.exception("Adzuna job search failed")



    return jobs
