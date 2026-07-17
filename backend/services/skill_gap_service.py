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
from skill_gap import skill_gap_analysis


class ProfileRequiredError(Exception):
    pass


class SkillGapError(Exception):
    pass


class SkillGapService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        job_catalog_repository: JobCatalogRepository,
        resume_analysis_repository: ResumeAnalysisRepository,
        analyzer: Callable[..., dict[str, Any]] = (
            skill_gap_analysis
        ),
    ):
        self.profile_repository = profile_repository
        self.job_catalog_repository = job_catalog_repository
        self.resume_analysis_repository = resume_analysis_repository
        self.analyzer = analyzer

    def analyze_for_user(
        self,
        user_id: int,
    ) -> dict[str, Any]:
        profile = self.profile_repository.get_by_user_id(
            user_id
        )

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before analyzing "
                "skill gaps."
            )

        try:
            jobs = self.job_catalog_repository.list_jobs()
            resume_skills = (
                self.resume_analysis_repository
                .get_latest_skills_by_user_id(user_id)
            )
            skills = merge_candidate_skills(profile, resume_skills)
            result = self.analyzer(
                profile_with_skills(profile, skills),
                jobs,
            )
        except Exception as error:
            raise SkillGapError(
                "Skill-gap analysis is temporarily unavailable."
            ) from error

        return {
            "current_skills": list(
                result.get("current_skills") or []
            ),
            "missing_skills": list(
                result.get("missing_skills") or []
            ),
            "recommendation": str(
                result.get("recommendation", "")
            ),
        }
