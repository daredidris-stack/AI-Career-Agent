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
from backend.repositories.career_document_repository import CareerDocumentRepository
from backend.repositories.job_application_repository import JobApplicationRepository
from backend.repositories.ai_usage_repository import AIUsageRepository
from backend.core.time import utc_now
from datetime import timedelta


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
        document_repository: CareerDocumentRepository | None = None,
        application_repository: JobApplicationRepository | None = None,
        ai_usage_repository: AIUsageRepository | None = None,
    ):
        self.profile_repository = profile_repository
        self.job_catalog_repository = job_catalog_repository
        self.resume_analysis_repository = resume_analysis_repository
        self.analyzer = analyzer
        self.document_repository = document_repository
        self.application_repository = application_repository
        self.ai_usage_repository = ai_usage_repository

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
            "weekly_progress": self._resume_progress(user_id),
            "document_counts": (
                self.document_repository.counts_by_kind(user_id)
                if self.document_repository and user_id is not None else {}
            ),
            "application_pipeline": (
                self.application_repository.counts_by_status(user_id)
                if self.application_repository and user_id is not None else {}
            ),
            "ai_requests_30d": (
                self.ai_usage_repository.count_since(
                    user_id, utc_now() - timedelta(days=30)
                )
                if self.ai_usage_repository and user_id is not None else 0
            ),
        }

    def _resume_progress(self, user_id: int | None) -> list[dict[str, Any]]:
        if user_id is None:
            return []
        history = self.resume_analysis_repository.list_for_user(
            user_id, limit=8
        )
        if not isinstance(history, list):
            return []
        analyses = reversed(history)
        return [
            {
                "week": analysis.created_at.strftime("%b %d"),
                "score": analysis.resume_score,
                "ats_score": analysis.ats_score,
            }
            for analysis in analyses
        ]

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
