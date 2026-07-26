from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_DIRECTORY = PROJECT_ROOT / "backend" / "templates"
DEFAULT_RESUME_TEMPLATE_ID = "ats-professional"
AUTO_RESUME_TEMPLATE_ID = "auto"


_RESUME_TEMPLATES: tuple[dict[str, Any], ...] = (
    {
        "id": "ats-professional",
        "name": "ATS Professional",
        "description": (
            "A polished navy and blue layout for technical, operations, "
            "business, and corporate roles."
        ),
        "filename": "ats_tailored_resume_template.docx",
        "accent": "#2E74B5",
        "font_style": "Clean sans serif",
        "recommended_for": ["Technology", "Operations", "Corporate"],
    },
    {
        "id": "ats-modern",
        "name": "ATS Modern",
        "description": (
            "A contemporary teal layout for product, engineering, data, "
            "startup, and creative-technical roles."
        ),
        "filename": "ats_modern_resume_template.docx",
        "accent": "#0F766E",
        "font_style": "Modern sans serif",
        "recommended_for": ["Engineering", "Data", "Product"],
    },
    {
        "id": "ats-classic",
        "name": "ATS Classic",
        "description": (
            "A traditional monochrome layout for leadership, finance, "
            "legal, education, and formal applications."
        ),
        "filename": "ats_classic_resume_template.docx",
        "accent": "#171717",
        "font_style": "Traditional serif",
        "recommended_for": ["Leadership", "Finance", "Education"],
    },
)


def list_resume_templates() -> list[dict[str, Any]]:
    return [
        {
            key: value
            for key, value in template.items()
            if key != "filename"
        }
        | {"is_default": template["id"] == DEFAULT_RESUME_TEMPLATE_ID}
        for template in _RESUME_TEMPLATES
    ]


def template_prompt_options() -> str:
    return "\n".join(
        f'- {template["id"]}: {template["description"]}'
        for template in _RESUME_TEMPLATES
    )


def validate_template_request(template_id: str | None) -> str:
    normalized = str(template_id or AUTO_RESUME_TEMPLATE_ID).strip().casefold()
    valid_ids = {template["id"] for template in _RESUME_TEMPLATES}
    if normalized != AUTO_RESUME_TEMPLATE_ID and normalized not in valid_ids:
        raise ValueError("Choose a valid resume template.")
    return normalized


def resolve_resume_template_id(
    requested_template_id: str | None,
    agent_template_id: str | None = None,
) -> str:
    requested = validate_template_request(requested_template_id)
    if requested != AUTO_RESUME_TEMPLATE_ID:
        return requested

    agent_choice = str(agent_template_id or "").strip().casefold()
    valid_ids = {template["id"] for template in _RESUME_TEMPLATES}
    if agent_choice in valid_ids:
        return agent_choice
    return DEFAULT_RESUME_TEMPLATE_ID


def resume_template_path(template_id: str | None) -> Path:
    resolved = resolve_resume_template_id(template_id)
    template = next(
        item for item in _RESUME_TEMPLATES if item["id"] == resolved
    )
    return TEMPLATE_DIRECTORY / template["filename"]
