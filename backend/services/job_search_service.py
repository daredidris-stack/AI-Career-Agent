import logging
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
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
from backend.core.settings import AI_JOB_RANKING_ENABLED
from backend.repositories.job_listing_repository import JobListingRepository


logger = logging.getLogger(__name__)


class JobSearchInputError(Exception):
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
        enable_ai_ranking: bool | None = None,
        job_listing_repository: JobListingRepository | None = None,
    ):
        self.profile_repository = profile_repository
        self.resume_analysis_repository = resume_analysis_repository
        self.job_aggregator = job_aggregator
        self.job_ranker = job_ranker
        self.job_listing_repository = job_listing_repository
        self.enable_ai_ranking = (
            AI_JOB_RANKING_ENABLED
            if enable_ai_ranking is None and job_ranker is rank_jobs
            else True if enable_ai_ranking is None else enable_ai_ranking
        )

    def search_for_user(
        self,
        user_id: int,
        keyword: str | None = None,
        country: str | None = None,
        city: str | None = None,
        industry: str | None = None,
        work_mode: str | None = None,
        employment_type: str | None = None,
        posted_within_days: int = 0,
        min_salary: int = 0,
        min_score: int = 0,
        page: int = 1,
        per_page: int = 50,
    ) -> dict[str, Any]:
        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        effective_keyword = (
            (keyword or "").strip()
            or (getattr(profile, "target_role", "") or "").strip()
            or (getattr(profile, "current_role", "") or "").strip()
        )
        effective_country = (country or "").strip() or "Worldwide"
        effective_city = (city or "").strip()
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
            raise JobSearchInputError(
                "Enter a target role before searching for jobs."
            )

        page = max(1, page)
        per_page = max(5, min(50, per_page))

        try:
            jobs = self._stored_jobs(
                effective_keyword,
                effective_location,
                page,
                per_page,
            )
            if jobs:
                provider_status = self._stored_provider_status(jobs)
            else:
                jobs = self.job_aggregator(
                    effective_keyword,
                    effective_location,
                    effective_industry,
                    page,
                    per_page,
                )
                provider_status = getattr(jobs, "provider_status", [])
                self._store_live_jobs(jobs)
            jobs = self._apply_listing_filters(
                jobs,
                employment_type,
                posted_within_days,
                min_salary,
            )
            resume_skills = (
                self.resume_analysis_repository
                .get_latest_skills_by_user_id(user_id)
            )
            candidate_profile = profile_with_skills(
                profile,
                merge_candidate_skills(profile, resume_skills),
            )

            jobs = self._pre_rank(
                jobs,
                candidate_profile["technical_skills"],
                effective_keyword,
            )
            provider_count = len(jobs)
            if self.enable_ai_ranking:
                ai_candidates = jobs[:5]
                remaining_jobs = jobs[5:]
                ranked_jobs = list(
                    self.job_ranker(candidate_profile, ai_candidates)
                )
                jobs = ranked_jobs + [
                    self._without_ai_score(job)
                    for job in remaining_jobs
                ]
            else:
                jobs = [
                    self._deterministic_analysis(
                        job,
                        candidate_profile["technical_skills"],
                        effective_keyword,
                    )
                    for job in jobs
                ]
        except Exception as error:
            raise JobSearchError(
                "Job search is temporarily unavailable."
            ) from error

        if min_score > 0:
            jobs = [
                job
                for job in jobs
                if (
                    (job.get("analysis") or {}).get("match_score") or 0
                ) >= min_score
            ]

        return {
            "count": len(jobs),
            "page": page,
            "per_page": per_page,
            "has_more": provider_count >= per_page,
            "providers": provider_status,
            "filters": {
                "keyword": effective_keyword,
                "location": effective_location,
                "country": effective_country,
                "city": effective_city,
                "industry": effective_industry,
                "work_mode": effective_work_mode,
                "employment_type": employment_type or "",
                "posted_within_days": max(0, posted_within_days),
                "minimum_salary": max(0, min_salary),
                "minimum_score": min_score,
            },
            "jobs": jobs,
        }

    def _stored_jobs(
        self,
        keyword: str,
        location: str,
        page: int,
        per_page: int,
    ) -> list[dict[str, Any]]:
        if self.job_listing_repository is None:
            return []
        try:
            return self.job_listing_repository.search(
                keyword,
                location,
                page,
                per_page,
            )
        except Exception:
            logger.warning("Stored job search failed; using live providers")
            self.job_listing_repository.rollback()
            return []

    def _store_live_jobs(self, jobs: list[dict[str, Any]]) -> None:
        if self.job_listing_repository is None or not jobs:
            return
        try:
            self.job_listing_repository.upsert_many(list(jobs))
        except Exception:
            logger.warning("Could not persist live job results")
            self.job_listing_repository.rollback()

    @staticmethod
    def _stored_provider_status(
        jobs: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        providers: dict[str, dict[str, Any]] = {}
        for job in jobs:
            name = str(job.get("source") or "Stored catalog")
            status = providers.setdefault(name, {
                "name": name,
                "status": "active",
                "count": 0,
                "homepage": str(job.get("source_homepage") or ""),
                "api_page": str(job.get("source_api_page") or ""),
                "cached": True,
            })
            status["count"] += 1
        return list(providers.values())

    @staticmethod
    def _pre_rank(
        jobs: list[dict[str, Any]],
        skills: list[str],
        keyword: str,
    ) -> list[dict[str, Any]]:
        def relevance(job: dict[str, Any]) -> int:
            text = " ".join([
                str(job.get("title") or ""),
                str(job.get("description") or ""),
                " ".join(str(value) for value in job.get("skills") or []),
            ]).casefold()
            score = 10 if keyword.casefold() in text else 0
            return score + sum(
                1 for skill in skills if skill.casefold() in text
            )

        return sorted(jobs, key=relevance, reverse=True)

    @staticmethod
    def _without_ai_score(job: dict[str, Any]) -> dict[str, Any]:
        job["analysis"] = {
            "match_score": None,
            "strengths": [],
            "missing_skills": [],
            "recommendation": "Open the listing to review full details.",
        }
        return job

    @staticmethod
    def _deterministic_analysis(
        job: dict[str, Any], skills: list[str], keyword: str
    ) -> dict[str, Any]:
        title = str(job.get("title") or "").casefold()
        searchable = " ".join([
            title,
            str(job.get("description") or "").casefold(),
            " ".join(str(value) for value in job.get("skills") or []).casefold(),
        ])
        role_terms = [term for term in keyword.casefold().split() if len(term) > 2]
        role_hits = sum(term in title for term in role_terms)
        matching_skills = [skill for skill in skills if skill.casefold() in searchable]
        role_score = round(50 * role_hits / max(1, len(role_terms)))
        skill_score = round(50 * len(matching_skills) / max(1, len(skills)))
        score = max(0, min(100, role_score + skill_score))
        job["analysis"] = {
            "match_score": score,
            "strengths": matching_skills,
            "missing_skills": [],
            "recommendation": (
                "Profile-based score calculated instantly. Open the listing "
                "to verify requirements and full details."
            ),
        }
        return job

    @classmethod
    def _apply_listing_filters(
        cls,
        jobs: list[dict[str, Any]],
        employment_type: str | None,
        posted_within_days: int,
        min_salary: int,
    ) -> list[dict[str, Any]]:
        filtered = jobs
        if employment_type:
            expected = employment_type.casefold().replace("-", " ")
            filtered = [
                job for job in filtered
                if expected in str(job.get("job_type") or "")
                .casefold().replace("-", " ")
            ]
        if min_salary > 0:
            filtered = [
                job for job in filtered
                if (job.get("salary_min") or 0) >= min_salary
            ]
        if posted_within_days > 0:
            cutoff = datetime.now(timezone.utc) - timedelta(
                days=posted_within_days
            )
            filtered = [
                job for job in filtered
                if (posted := cls._posted_at(job.get("updated")))
                and posted >= cutoff
            ]
        return filtered

    @staticmethod
    def _posted_at(value: Any) -> datetime | None:
        if isinstance(value, (int, float)):
            timestamp = value / 1000 if value > 10_000_000_000 else value
            return datetime.fromtimestamp(timestamp, tz=timezone.utc)
        if isinstance(value, str) and value.strip():
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
                return parsed.replace(tzinfo=parsed.tzinfo or timezone.utc)
            except ValueError:
                return None
        return None

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
            or "Worldwide"
