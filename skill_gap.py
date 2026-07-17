from collections.abc import Iterable, Mapping
from typing import Any

from services.ollama_service import ask_llm


PRIORITY_SKILLS = [
    "Docker",
    "Terraform",
    "CI/CD",
    "Kubernetes",
    "Python Automation (Boto3)",
    "Machine Learning (Optional)",
]


def _get_profile_value(
    profile: Mapping[str, Any] | Any,
    field_name: str,
    default: Any = None,
) -> Any:
    if isinstance(profile, Mapping):
        return profile.get(field_name, default)

    return getattr(profile, field_name, default)


def _normalize_skills(skills: Any) -> list[str]:
    if not skills:
        return []

    if isinstance(skills, str):
        values: Iterable[Any] = skills.split(",")
    elif isinstance(skills, Iterable):
        values = skills
    else:
        values = [skills]

    normalized_skills = []
    seen = set()

    for skill in values:
        normalized_skill = str(skill).strip()
        comparison_key = normalized_skill.casefold()

        if normalized_skill and comparison_key not in seen:
            normalized_skills.append(normalized_skill)
            seen.add(comparison_key)

    return normalized_skills


def _job_skills(jobs: Any) -> list[str]:
    if not isinstance(jobs, list):
        return []

    required_skills = []

    for job in jobs:
        if not isinstance(job, Mapping):
            continue

        required_skills.extend(
            _normalize_skills(job.get("skills"))
        )

    return _normalize_skills(required_skills)


def _prioritize_missing_skills(
    required_skills: list[str],
    current_skills: list[str],
) -> list[str]:
    current_skill_keys = {
        skill.casefold()
        for skill in current_skills
    }
    missing_skills = [
        skill
        for skill in required_skills
        if skill.casefold() not in current_skill_keys
    ]

    priority_positions = {
        skill.casefold(): position
        for position, skill in enumerate(PRIORITY_SKILLS)
    }

    return sorted(
        missing_skills,
        key=lambda skill: (
            priority_positions.get(
                skill.casefold(),
                len(priority_positions),
            ),
            skill.casefold(),
        ),
    )


def skill_gap_analysis(
    profile: Mapping[str, Any] | Any | None,
    jobs: Any,
) -> dict[str, Any]:
    """Analyze gaps using normalized database profile fields."""
    profile = profile or {}

    current_skills = _normalize_skills(
        _get_profile_value(profile, "technical_skills")
    )
    years_experience = (
        _get_profile_value(profile, "years_experience", 0)
        or 0
    )
    current_role = (
        _get_profile_value(profile, "current_role", "")
        or "Not provided"
    )
    target_role = (
        _get_profile_value(profile, "target_role", "")
        or "Not provided"
    )
    professional_summary = (
        _get_profile_value(
            profile,
            "professional_summary",
            "",
        )
        or "Not provided"
    )

    required_skills = _job_skills(jobs)
    missing_skills = _prioritize_missing_skills(
        required_skills,
        current_skills,
    )

    current_skills_text = (
        ", ".join(current_skills)
        or "Not provided"
    )
    missing_skills_text = (
        ", ".join(missing_skills)
        or "No gaps identified from the available jobs"
    )

    prompt = f"""
You are a senior career advisor.

Analyze this candidate's skill gaps using only the supplied profile and job data.

Candidate profile:
- Current role: {current_role}
- Target role: {target_role}
- Years of experience: {years_experience}
- Professional summary: {professional_summary}
- Current technical skills: {current_skills_text}

Skills required by the available jobs but not present in the profile:
{missing_skills_text}

Return:
- Current skills
- Missing skills
- Recommended learning order
- Career impact
- Recommended projects
""".strip()

    recommendation = ask_llm(prompt)

    return {
        "current_skills": current_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
    }
