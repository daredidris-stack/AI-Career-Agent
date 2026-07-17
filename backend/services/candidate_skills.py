from typing import Any


PROFILE_SKILL_CONTEXT_FIELDS = (
    "current_role",
    "target_role",
    "years_experience",
    "professional_summary",
)


def normalize_explicit_skills(skills: Any) -> list[str]:
    if isinstance(skills, str):
        values = [skills]
    elif isinstance(skills, list):
        values = skills
    else:
        return []

    normalized = []
    seen = set()

    for item in values:
        for skill in str(item).split(","):
            value = skill.strip()
            key = value.casefold()
            if value and key not in seen:
                normalized.append(value)
                seen.add(key)

    explicit_keys = {skill.casefold() for skill in normalized}
    if any(key.startswith("aws ") for key in explicit_keys):
        _append_unique(normalized, seen, "AWS")
    if "github actions" in explicit_keys:
        _append_unique(normalized, seen, "CI/CD")

    return normalized


def _append_unique(
    skills: list[str],
    seen: set[str],
    value: str,
) -> None:
    key = value.casefold()
    if key not in seen:
        skills.append(value)
        seen.add(key)


def merge_candidate_skills(
    profile: Any,
    resume_skills: list[str],
) -> list[str]:
    profile_skills = getattr(profile, "technical_skills", None) or ""
    return normalize_explicit_skills([
        profile_skills,
        *resume_skills,
    ])


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
