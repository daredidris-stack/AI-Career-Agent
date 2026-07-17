import json
import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_profile_service
from backend.models.user import User
from backend.services.profile_service import ProfileService
from skill_gap import skill_gap_analysis


logger = logging.getLogger(__name__)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
JOBS_FILE = PROJECT_ROOT / "jobs.json"


def load_jobs():
    if not JOBS_FILE.exists():
        return []

    with JOBS_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


@router.get("")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: ProfileService = Depends(get_profile_service),
):
    profile = service.get_profile(
        current_user.id
    )

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=(
                "Create your profile before "
                "viewing the dashboard."
            ),
        )

    jobs = load_jobs()

    technical_skills = convert_skills_to_list(
        getattr(
            profile,
            "technical_skills",
            None,
        )
    )

    soft_skills = convert_skills_to_list(
        getattr(
            profile,
            "soft_skills",
            None,
        )
    )

    user_name = (
        getattr(
            current_user,
            "name",
            "",
        )
        or getattr(
            current_user,
            "full_name",
            "",
        )
        or getattr(
            current_user,
            "email",
            "User",
        )
    )

    years_experience = (
        getattr(
            profile,
            "years_experience",
            0,
        )
        or 0
    )

    current_role = (
        getattr(
            profile,
            "current_role",
            "",
        )
        or ""
    )

    target_role = (
        getattr(
            profile,
            "target_role",
            "",
        )
        or ""
    )

    profile_data = {
        "name": user_name,
        "email": getattr(
            current_user,
            "email",
            "",
        ),
        "phone": (
            getattr(
                profile,
                "phone",
                "",
            )
            or ""
        ),
        "country": (
            getattr(
                profile,
                "country",
                "",
            )
            or ""
        ),
        "state": (
            getattr(
                profile,
                "state",
                "",
            )
            or ""
        ),
        "city": (
            getattr(
                profile,
                "city",
                "",
            )
            or ""
        ),
        "current_role": current_role,
        "target_role": target_role,
        "target_roles": (
            [target_role]
            if target_role
            else []
        ),
        "years_experience": years_experience,
        "experience": years_experience,
        "professional_summary": (
            getattr(
                profile,
                "professional_summary",
                "",
            )
            or ""
        ),
        "skills": technical_skills,
        "technical_skills": technical_skills,
        "soft_skills": soft_skills,
        "preferred_job_type": (
            getattr(
                profile,
                "preferred_job_type",
                "",
            )
            or ""
        ),
        "preferred_work_mode": (
            getattr(
                profile,
                "preferred_work_mode",
                "",
            )
            or ""
        ),
    }

    try:
        skill_report = skill_gap_analysis(
            profile_data,
            jobs,
        )
    except Exception:
        logger.exception(
            "Skill-gap analysis failed for user %s",
            current_user.id,
        )

        skill_report = {
            "current_skills": (
                technical_skills
            ),
            "missing_skills": [],
            "recommendation": "",
        }

    current_skills = skill_report.get(
        "current_skills",
        technical_skills,
    )

    if not isinstance(
        current_skills,
        list,
    ):
        current_skills = convert_skills_to_list(
            current_skills
        )

    missing_skills = skill_report.get(
        "missing_skills",
        [],
    )

    if not isinstance(
        missing_skills,
        list,
    ):
        missing_skills = (
            convert_skills_to_list(
                missing_skills
            )
        )

    if missing_skills:
        recommended_skill_name = (
            missing_skills[0]
        )

        recommended_skill_description = (
            f"Focus on "
            f"{recommended_skill_name} "
            "to improve your alignment "
            "with your target roles."
        )
    else:
        recommended_skill_name = (
            "Keep developing your "
            "strongest skills"
        )

        recommended_skill_description = (
            "Your core skills are well "
            "aligned. Continue building "
            "practical projects."
        )

    profile_completion = (
        calculate_profile_completion(
            profile
        )
    )

    dashboard_data = {
        "user": {
            "name": user_name,
            "email": getattr(
                current_user,
                "email",
                "",
            ),
        },
        "profile": {
            "current_role": current_role,
            "target_role": target_role,
            "city": (
                getattr(
                    profile,
                    "city",
                    "",
                )
                or ""
            ),
            "country": (
                getattr(
                    profile,
                    "country",
                    "",
                )
                or ""
            ),
            "preferred_job_type": (
                getattr(
                    profile,
                    "preferred_job_type",
                    "",
                )
                or ""
            ),
            "preferred_work_mode": (
                getattr(
                    profile,
                    "preferred_work_mode",
                    "",
                )
                or ""
            ),
            "completion": (
                profile_completion
            ),
        },
        "skill_gap": len(
            missing_skills
        ),
        "resume_score": 82,
        "job_matches": len(jobs),
        "ats_score": 88,
        "skills_completed": len(
            current_skills
        ),
        "career_progress": (
            profile_completion
        ),
        "recommended_skill": {
            "name": (
                recommended_skill_name
            ),
            "description": (
                recommended_skill_description
            ),
        },
        "technical_skills": (
            current_skills
        ),
        "missing_skills": (
            missing_skills
        ),
        "weekly_progress": [
            {
                "week": "Week 1",
                "score": 62,
            },
            {
                "week": "Week 2",
                "score": 70,
            },
            {
                "week": "Week 3",
                "score": 78,
            },
            {
                "week": "Week 4",
                "score": 82,
            },
        ],
        "recent_activity": [
            "Profile information loaded",
            "Career preferences analyzed",
            "Skill gap analysis completed",
            (
                "Dashboard recommendations "
                "updated"
            ),
        ],
    }

    return dashboard_data


def convert_skills_to_list(
    skills,
):
    if not skills:
        return []

    if isinstance(
        skills,
        list,
    ):
        return [
            str(skill).strip()
            for skill in skills
            if str(skill).strip()
        ]

    if isinstance(
        skills,
        set,
    ):
        return [
            str(skill).strip()
            for skill in skills
            if str(skill).strip()
        ]

    return [
        skill.strip()
        for skill in str(
            skills
        ).split(",")
        if skill.strip()
    ]


def calculate_profile_completion(
    profile,
):
    field_names = [
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
    ]

    fields = [
        getattr(
            profile,
            field_name,
            None,
        )
        for field_name in field_names
    ]

    completed_fields = sum(
        1
        for value in fields
        if value is not None
        and str(value).strip()
        not in {
            "",
            "0",
            "None",
        }
    )

    return round(
        completed_fields
        / len(fields)
        * 100
    )
