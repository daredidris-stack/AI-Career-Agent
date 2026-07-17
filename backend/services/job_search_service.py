from collections.abc import Callable
from typing import Any

from backend.repositories.profile_repository import ProfileRepository
from backend.services.job_aggregator import aggregate_jobs
from backend.services.job_ranking import rank_jobs


class ProfileRequiredError(Exception):
    pass


class JobSearchError(Exception):
    pass


class JobSearchService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        job_aggregator: Callable[..., list[dict]] = aggregate_jobs,
        job_ranker: Callable[..., list[dict]] = rank_jobs,
    ):
        self.profile_repository = profile_repository
        self.job_aggregator = job_aggregator
        self.job_ranker = job_ranker

    def search_for_user(
        self,
        user_id: int,
        keyword: str,
        location: str = "Remote",
        experience: str = "",
        min_score: int = 0,
        ai_rank: bool = True,
    ) -> dict[str, Any]:
        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before searching for jobs."
            )

        try:
            jobs = self.job_aggregator(keyword, location)

            if ai_rank:
                jobs = self.job_ranker(profile, jobs)
        except Exception as error:
            raise JobSearchError(
                "Job search is temporarily unavailable."
            ) from error

        if min_score > 0:
            jobs = [
                job
                for job in jobs
                if job.get("analysis", {}).get(
                    "match_score",
                    0,
                )
                >= min_score
            ]

        return {
            "count": len(jobs),
            "filters": {
                "keyword": keyword,
                "location": location,
                "experience": experience,
                "minimum_score": min_score,
            },
            "jobs": jobs,
        }
