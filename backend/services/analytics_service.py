from typing import Any, Callable

from backend.repositories.job_catalog_repository import (
    JobCatalogRepository,
)
from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)
from backend.services.candidate_skills import (
    merge_candidate_skills,
    profile_with_skills,
)
from skill_gap import calculate_skill_gap


PROFILE_COMPLETION_FIELDS = (
    "phone",
    "country",
    "state",
    "city",
    "current_role",
    "target_role",
    "years_experience",
    "professional_summary",
    "technical_skills",
    "soft_skills",
    "linkedin",
    "github",
    "portfolio",
    "preferred_job_type",
    "preferred_work_mode",
)


class ProfileRequiredError(Exception):
    pass


class AnalyticsError(Exception):
    pass


class AnalyticsService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        job_catalog_repository: JobCatalogRepository,
        resume_analysis_repository: ResumeAnalysisRepository,
        analyzer: Callable[..., dict[str, Any]] = calculate_skill_gap,
    ):
        self.profile_repository = profile_repository
        self.job_catalog_repository = job_catalog_repository
        self.resume_analysis_repository = resume_analysis_repository
        self.analyzer = analyzer

    def get_for_user(self, user_id: int) -> dict[str, Any]:
        profile = self.profile_repository.get_by_user_id(user_id)

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before viewing analytics."
            )

        return self.get_for_profile(profile, user_id)

    def get_for_profile(
        self,
        profile: Any,
        user_id: int | None = None,
    ) -> dict[str, Any]:
        try:
            jobs = self.job_catalog_repository.list_jobs()
            resume_skills = (
                self.resume_analysis_repository
                .get_latest_skills_by_user_id(user_id)
                if user_id is not None
                else []
            )
            skills = merge_candidate_skills(profile, resume_skills)
            skill_report = self.analyzer(
                profile_with_skills(profile, skills),
                jobs,
            )
        except Exception as error:
            raise AnalyticsError(
                "Career analytics are temporarily unavailable."
            ) from error

        current_skills = list(
            skill_report.get("current_skills") or []
        )
        missing_skills = list(
            skill_report.get("missing_skills") or []
        )

        return {
            "profile_completion": self._profile_completion(profile),
            "skills_completed": len(current_skills),
            "skill_gap": len(missing_skills),
            "jobs_available": len(jobs),
            "current_skills": current_skills,
            "missing_skills": missing_skills,
            "weekly_progress": [],
        }

    @staticmethod
    def _profile_completion(profile: Any) -> int:
        completed_fields = sum(
            1
            for field_name in PROFILE_COMPLETION_FIELDS
            if AnalyticsService._has_value(
                getattr(profile, field_name, None)
            )
        )

        return round(
            completed_fields / len(PROFILE_COMPLETION_FIELDS) * 100
        )

    @staticmethod
    def _has_value(value: Any) -> bool:
        return (
            value is not None
            and str(value).strip() not in {"", "0", "None"}
        )
