from typing import Any

from backend.repositories.profile_repository import ProfileRepository
from backend.services.analytics_service import (
    AnalyticsError,
    AnalyticsService,
)


class ProfileRequiredError(Exception):
    pass


class DashboardError(Exception):
    pass


class DashboardService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        analytics_service: AnalyticsService,
    ):
        self.profile_repository = profile_repository
        self.analytics_service = analytics_service

    def get_for_user(self, user: Any) -> dict[str, Any]:
        profile = self.profile_repository.get_by_user_id(user.id)

        if not profile:
            raise ProfileRequiredError(
                "Create your profile before viewing the dashboard."
            )

        try:
            analytics = self.analytics_service.get_for_profile(profile)
        except AnalyticsError as error:
            raise DashboardError(
                "Dashboard insights are temporarily unavailable."
            ) from error

        missing_skills = analytics["missing_skills"]
        recommended_skill = self._recommended_skill(missing_skills)

        return {
            "user": {
                "name": self._user_name(user),
                "email": getattr(user, "email", "") or "",
            },
            "profile": {
                "current_role": self._value(profile, "current_role"),
                "target_role": self._value(profile, "target_role"),
                "city": self._value(profile, "city"),
                "country": self._value(profile, "country"),
                "preferred_job_type": self._value(
                    profile,
                    "preferred_job_type",
                ),
                "preferred_work_mode": self._value(
                    profile,
                    "preferred_work_mode",
                ),
                "completion": analytics["profile_completion"],
            },
            "skill_gap": analytics["skill_gap"],
            "resume_score": None,
            "jobs_available": analytics["jobs_available"],
            "ats_score": None,
            "skills_completed": analytics["skills_completed"],
            "career_progress": analytics["profile_completion"],
            "recommended_skill": recommended_skill,
            "technical_skills": analytics["current_skills"],
            "missing_skills": missing_skills,
            "weekly_progress": analytics["weekly_progress"],
            "recent_activity": [],
        }

    @staticmethod
    def _value(instance: Any, field_name: str) -> Any:
        return getattr(instance, field_name, None) or ""

    @staticmethod
    def _user_name(user: Any) -> str:
        full_name = " ".join(
            part
            for part in (
                getattr(user, "first_name", "") or "",
                getattr(user, "last_name", "") or "",
            )
            if part
        )
        return full_name or getattr(user, "email", "User") or "User"

    @staticmethod
    def _recommended_skill(missing_skills: list[str]) -> dict[str, str]:
        if missing_skills:
            name = missing_skills[0]
            return {
                "name": name,
                "description": (
                    f"Focus on {name} to improve your alignment "
                    "with your target roles."
                ),
            }

        return {
            "name": "Keep developing your strongest skills",
            "description": (
                "Your core skills are well aligned. Continue building "
                "practical projects."
            ),
        }
