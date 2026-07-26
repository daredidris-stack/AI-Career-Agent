import asyncio
import json
import re
from datetime import date
from typing import Any
from urllib.parse import urlparse

from fastapi import UploadFile

from backend.services.resume_service import ResumeService
from resume_text_cleaner import clean_resume_text
from services.ollama_service import reliable_chat


PROFILE_FIELDS = (
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
TEXT_LIMITS = {
    "country": 100,
    "state": 100,
    "city": 100,
    "current_role": 200,
    "target_role": 200,
    "professional_summary": 2000,
    "technical_skills": 2000,
    "soft_skills": 2000,
}
URL_FIELDS = ("linkedin", "github", "portfolio")
JOB_TYPES = {
    value.casefold(): value
    for value in (
        "Full-time",
        "Part-time",
        "Contract",
        "Internship",
        "Freelance",
    )
}
WORK_MODES = {
    value.casefold(): value
    for value in ("Remote", "Hybrid", "On-site", "Flexible")
}
PLACEHOLDER_VALUES = {
    "n/a",
    "na",
    "none",
    "not provided",
    "unknown",
    "example",
}
MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}
MONTH_PATTERN = "|".join(sorted(MONTHS, key=len, reverse=True))
DATE_RANGE_PATTERN = re.compile(
    rf"(?:(?P<start_month>{MONTH_PATTERN})\.?\s+)?"
    r"(?P<start_year>(?:19|20)\d{2})\s*"
    r"(?:-|–|—|to)\s*"
    rf"(?:(?:(?P<end_month>{MONTH_PATTERN})\.?\s+)?"
    r"(?P<end_year>(?:19|20)\d{2})|"
    r"(?P<present>present|current|now))",
    re.IGNORECASE,
)


class ProfileAutofillService:
    def __init__(self, resume_service: ResumeService):
        self.resume_service = resume_service

    async def autofill_upload(self, file: UploadFile) -> dict[str, Any]:
        resume_text = await self.resume_service.extract_text(file)
        cleaned_resume_text = clean_resume_text(resume_text)
        try:
            raw_result = await asyncio.to_thread(
                extract_profile_from_resume,
                cleaned_resume_text,
            )
        except Exception as error:
            raise ProfileAutofillError(
                "Profile autofill is temporarily unavailable."
            ) from error

        return normalize_profile_autofill(
            raw_result,
            resume_text=resume_text,
        )


def extract_profile_from_resume(resume_text: str) -> dict[str, Any]:
    resume_text = clean_resume_text(resume_text)
    prompt = f"""
You extract a candidate profile from a resume.
Today's date is {date.today().isoformat()}.

Resume:
{resume_text}

Return ONLY one valid JSON object with these exact keys:
{{
  "phone": "",
  "country": "",
  "state": "",
  "city": "",
  "current_role": "",
  "target_role": "",
  "years_experience": null,
  "professional_summary": "",
  "technical_skills": [],
  "soft_skills": [],
  "linkedin": "",
  "github": "",
  "portfolio": "",
  "preferred_job_type": "",
  "preferred_work_mode": ""
}}

Rules:
- Use only information supported by the resume. Never invent details.
- Ignore template instructions, optional-section notes, example contact details,
  and commentary written by a resume generator.
- Treat example.com email addresses and North American 555 phone numbers as
  placeholders, not candidate data.
- Use the most recent position for current_role.
- If a Target Roles or objective section explicitly lists multiple roles, use
  the first role for target_role.
- years_experience must be a whole number or null. Estimate it conservatively
  from clearly dated work history and do not double-count overlapping roles.
- Write professional_summary as two to four concise sentences based only on
  the resume.
- Return technical_skills and soft_skills as JSON arrays of individual skills.
  Omit category labels such as "Programming" or "Other".
- Soft skills may be extracted from explicit evidence such as collaboration,
  communication, leadership, mentoring, or cross-functional teamwork.
- Leave job preferences empty unless explicitly stated.
- Leave every unknown field as an empty string or null.
"""
    response = reliable_chat(prompt, response_format="json")
    text = response.message.content
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("Profile autofill did not return JSON.")
    return json.loads(match.group())


def normalize_profile_autofill(
    result: Any,
    *,
    resume_text: str = "",
) -> dict[str, Any]:
    if not isinstance(result, dict):
        raise ProfileAutofillError("Profile autofill returned invalid data.")

    normalized: dict[str, Any] = {field: None for field in PROFILE_FIELDS}
    for field, limit in TEXT_LIMITS.items():
        value = result.get(field)
        if isinstance(value, list):
            value = ", ".join(
                str(item).strip()
                for item in value
                if item is not None and str(item).strip()
            )
        if value is not None:
            text = str(value).strip()
            normalized[field] = (
                text[:limit]
                if text and text.casefold() not in PLACEHOLDER_VALUES
                else None
            )

    normalized["phone"] = _normalize_phone(result.get("phone"))

    for field in URL_FIELDS:
        normalized[field] = _normalize_url(result.get(field))

    years = result.get("years_experience")
    try:
        normalized["years_experience"] = (
            max(0, min(80, int(float(years))))
            if years not in (None, "")
            else None
        )
    except (TypeError, ValueError):
        normalized["years_experience"] = None

    calculated_years = calculate_experience_years(resume_text)
    if calculated_years is not None:
        normalized["years_experience"] = calculated_years

    target_role_options = extract_target_role_options(resume_text)
    if target_role_options:
        selected_target = str(normalized.get("target_role") or "").casefold()
        option_keys = {option.casefold() for option in target_role_options}
        if selected_target not in option_keys:
            normalized["target_role"] = target_role_options[0]

    normalized["preferred_job_type"] = _normalize_choice(
        result.get("preferred_job_type"), JOB_TYPES
    )
    normalized["preferred_work_mode"] = _normalize_choice(
        result.get("preferred_work_mode"), WORK_MODES
    )
    warnings = []
    if result.get("phone") and normalized["phone"] is None:
        warnings.append("A placeholder or invalid phone number was ignored.")
    if _contains_template_notes(resume_text):
        warnings.append("Template instructions and optional-section notes were ignored.")

    normalized["extracted_fields"] = [
        field for field in PROFILE_FIELDS if normalized.get(field) is not None
    ]
    normalized["target_role_options"] = target_role_options
    normalized["warnings"] = warnings
    return normalized


def extract_target_role_options(resume_text: str) -> list[str]:
    section = _extract_section(
        resume_text,
        ("target role", "target roles", "career objective"),
    )
    if not section:
        return []

    roles = []
    seen = set()
    for value in re.split(r"[,;\n]", section):
        role = value.strip().strip("-•")
        key = role.casefold()
        if role and len(role) <= 100 and key not in seen:
            roles.append(role)
            seen.add(key)
    return roles[:10]


def calculate_experience_years(
    resume_text: str,
    *,
    today: date | None = None,
) -> int | None:
    experience = _extract_section(
        resume_text,
        (
            "professional experience",
            "work experience",
            "employment history",
            "employment",
        ),
    )
    if not experience:
        return None

    current_date = today or date.today()
    intervals = []
    for match in DATE_RANGE_PATTERN.finditer(experience):
        start_year = int(match.group("start_year"))
        start_month = _month_number(match.group("start_month"), default=1)
        start = start_year * 12 + start_month - 1

        if match.group("present"):
            end = current_date.year * 12 + current_date.month - 1
        else:
            end_year = int(match.group("end_year"))
            end_month = _month_number(match.group("end_month"), default=12)
            end = end_year * 12 + end_month

        if end > start:
            intervals.append((start, end))

    if not intervals:
        return None

    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))

    total_months = sum(end - start for start, end in merged)
    return max(0, min(80, total_months // 12))


def _extract_section(resume_text: str, headings: tuple[str, ...]) -> str:
    lines = str(resume_text or "").splitlines()
    normalized_headings = {heading.casefold() for heading in headings}
    start_index = None
    for index, line in enumerate(lines):
        if line.strip().strip(":").casefold() in normalized_headings:
            start_index = index + 1
            break
    if start_index is None:
        return ""

    section_lines = []
    for line in lines[start_index:]:
        value = line.strip().strip(":")
        if section_lines and _looks_like_section_heading(value):
            break
        section_lines.append(line)
    return "\n".join(section_lines).strip()


def _looks_like_section_heading(value: str) -> bool:
    known_headings = {
        "education",
        "professional experience",
        "work experience",
        "employment history",
        "technical skills",
        "skills",
        "soft skills",
        "target role",
        "target roles",
        "career objective",
        "projects",
        "projects (optional)",
        "certifications",
        "certifications (optional)",
        "awards",
        "languages",
        "references",
    }
    return value.casefold() in known_headings


def _month_number(value: str | None, *, default: int) -> int:
    if not value:
        return default
    return MONTHS.get(value.casefold().rstrip("."), default)


def _normalize_phone(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    text = value.strip()
    if not text or text.casefold() in PLACEHOLDER_VALUES:
        return None
    digits = re.sub(r"\D", "", text)
    if len(digits) == 10 and digits.startswith("555"):
        return None
    if len(digits) == 11 and digits.startswith("1555"):
        return None
    if len(digits) < 7 or len(digits) > 15:
        return None
    return text[:100]


def _contains_template_notes(resume_text: str) -> bool:
    text = str(resume_text or "").casefold()
    return any(
        marker in text
        for marker in (
            "projects (optional)",
            "certifications (optional)",
            "include relevant projects if applicable",
            "add certifications like",
            "this resume emphasizes",
        )
    )


def _normalize_choice(value: Any, choices: dict[str, str]) -> str | None:
    if not isinstance(value, str):
        return None
    return choices.get(value.strip().casefold())


def _normalize_url(value: Any) -> str | None:
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text or text.casefold() in PLACEHOLDER_VALUES:
        return None
    if not re.match(r"^https?://", text, re.IGNORECASE):
        text = f"https://{text.lstrip('/')}"

    parsed = urlparse(text)
    if (
        parsed.scheme.casefold() not in {"http", "https"}
        or not parsed.netloc
        or " " in parsed.netloc
    ):
        return None
    return text[:500]


class ProfileAutofillError(Exception):
    pass
