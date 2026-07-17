from collections.abc import Callable
from typing import Any

from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)
from backend.services.candidate_skills import (
    merge_candidate_skills,
    profile_with_skills,
)
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
        resume_analysis_repository: ResumeAnalysisRepository,
        job_aggregator: Callable[..., list[dict]] = aggregate_jobs,
        job_ranker: Callable[..., list[dict]] = rank_jobs,
    ):
        self.profile_repository = profile_repository
        self.resume_analysis_repository = resume_analysis_repository
        self.job_aggregator = job_aggregator
        self.job_ranker = job_ranker

    def search_for_user(
        self,
        user_id: int,
        keyword: str | None = None,
        country: str | None = None,
        city: str | None = None,
        industry: str | None = None,
        work_mode: str | None = None,
        min_score: int = 0,
    ) -> dict[str, Any]:
        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before searching for jobs."
            )

        effective_keyword = (
            (keyword or "").strip()
            or (getattr(profile, "target_role", "") or "").strip()
            or (getattr(profile, "current_role", "") or "").strip()
        )
        effective_country = (
            (country or "").strip()
            or (getattr(profile, "country", "") or "").strip()
        )
        effective_city = (
            (city or "").strip()
            or (getattr(profile, "city", "") or "").strip()
        )
        effective_work_mode = (
            (work_mode or "").strip()
            or (
                getattr(profile, "preferred_work_mode", "") or ""
            ).strip()
        )
        effective_industry = (industry or "").strip()
        effective_location = self._search_location(
            effective_city,
            effective_country,
            effective_work_mode,
        )

        if not effective_keyword:
            raise JobSearchError(
                "Add a target role to your profile before searching."
            )

        try:
            jobs = self.job_aggregator(
                effective_keyword,
                effective_location,
                effective_industry,
            )
            resume_skills = (
                self.resume_analysis_repository
                .get_latest_skills_by_user_id(user_id)
            )
            candidate_profile = profile_with_skills(
                profile,
                merge_candidate_skills(profile, resume_skills),
            )

            jobs = self.job_ranker(candidate_profile, jobs)
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
                "keyword": effective_keyword,
                "location": effective_location,
                "country": effective_country,
                "city": effective_city,
                "industry": effective_industry,
                "work_mode": effective_work_mode,
                "minimum_score": min_score,
            },
            "jobs": jobs,
        }

    @staticmethod
    def _search_location(
        city: str,
        country: str,
        work_mode: str,
    ) -> str:
        if country.casefold() == "worldwide":
            return "Worldwide"

        if work_mode.casefold() == "remote":
            return "Remote"

        return ", ".join(value for value in (city, country) if value) \
            or "Remote"
