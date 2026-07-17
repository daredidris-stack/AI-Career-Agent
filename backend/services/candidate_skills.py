from typing import Any


PROFILE_SKILL_CONTEXT_FIELDS = (
    "current_role",
    "target_role",
    "years_experience",
    "professional_summary",
)


def merge_candidate_skills(
    profile: Any,
    resume_skills: list[str],
) -> list[str]:
    profile_skills = getattr(profile, "technical_skills", None) or ""
    if not isinstance(resume_skills, list):
        resume_skills = []
    values = [
        *str(profile_skills).split(","),
        *resume_skills,
    ]
    merged = []
    seen = set()

    for skill in values:
        value = str(skill).strip()
        key = value.casefold()
        if value and key not in seen:
            merged.append(value)
            seen.add(key)

    return merged


def profile_with_skills(
    profile: Any,
    skills: list[str],
) -> dict[str, Any]:
    context = {
        field_name: getattr(profile, field_name, None)
        for field_name in PROFILE_SKILL_CONTEXT_FIELDS
    }
    context["technical_skills"] = skills
    return context
