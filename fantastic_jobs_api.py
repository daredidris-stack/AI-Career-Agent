import copy
from threading import Lock
from time import monotonic
from typing import Any

import requests

from backend.core.settings import (
    FANTASTIC_JOBS_API_KEY,
    FANTASTIC_JOBS_CACHE_SECONDS,
    FANTASTIC_JOBS_MAX_RESULTS,
    FANTASTIC_JOBS_TIME_FRAME,
)


FANTASTIC_JOBS_URL = "https://data.fantastic.jobs/v1/active-ats"
_CACHE: dict[
    tuple[str, str, int, int, str],
    tuple[float, list[dict[str, Any]]],
] = {}
_CACHE_LOCK = Lock()


def search_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
    time_frame: str | None = None,
) -> list[dict[str, Any]]:
    """Search Fantastic.jobs' direct-employer ATS index.

    Fantastic.jobs charges by returned job, so each response is capped and
    cached briefly to avoid spending credits on repeated identical searches.
    """
    if not FANTASTIC_JOBS_API_KEY:
        return []

    page_number = max(1, page)
    page_size = min(max(1, results), FANTASTIC_JOBS_MAX_RESULTS)
    normalized_keyword = str(keyword or "").strip()
    normalized_location = str(location or "").strip()
    selected_time_frame = (
        time_frame
        if time_frame in {"1h", "24h", "7d", "6m"}
        else FANTASTIC_JOBS_TIME_FRAME
    )
    cache_key = (
        normalized_keyword.casefold(),
        normalized_location.casefold(),
        page_number,
        page_size,
        selected_time_frame,
    )
    cached = _cached_jobs(cache_key)
    if cached is not None:
        return cached

    params: dict[str, Any] = {
        "time_frame": selected_time_frame,
        "limit": page_size,
        "offset": (page_number - 1) * page_size,
        "description_format": "text",
    }
    if normalized_keyword:
        params["title"] = normalized_keyword
    location_key = normalized_location.casefold()
    if location_key == "remote":
        params["ai_work_arrangement"] = "Remote Solely,Remote OK"
    elif location_key not in {"", "worldwide"}:
        params["location"] = normalized_location

    try:
        response = requests.get(
            FANTASTIC_JOBS_URL,
            headers={
                "Authorization": f"Bearer {FANTASTIC_JOBS_API_KEY}",
                "Accept": "application/json",
            },
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError("Employer index request failed.") from None

    if not isinstance(data, list):
        raise RuntimeError("Employer index returned invalid data.")

    jobs = [
        normalized
        for item in data
        if isinstance(item, dict)
        for normalized in [_normalize_job(item)]
        if normalized["title"] and normalized["url"]
    ]
    with _CACHE_LOCK:
        _CACHE[cache_key] = (
            monotonic() + FANTASTIC_JOBS_CACHE_SECONDS,
            copy.deepcopy(jobs),
        )
    return jobs


def _cached_jobs(
    cache_key: tuple[str, str, int, int, str],
) -> list[dict[str, Any]] | None:
    now = monotonic()
    with _CACHE_LOCK:
        cached = _CACHE.get(cache_key)
        if cached is None:
            return None
        expires_at, jobs = cached
        if expires_at <= now:
            _CACHE.pop(cache_key, None)
            return None
        return copy.deepcopy(jobs)


def _normalize_job(item: dict[str, Any]) -> dict[str, Any]:
    apply_url = str(item.get("url") or "").strip()
    arrangement = str(item.get("ai_work_arrangement") or "").strip()
    location = _location(item, arrangement)
    salary, salary_min, salary_max = _salary(item)
    employment_types = _strings(
        item.get("ai_employment_type") or item.get("employment_type")
    )
    skills = _strings(item.get("ai_key_skills") or item.get("ai_keywords"))
    return {
        "source_job_id": str(item.get("id") or ""),
        "title": str(item.get("title") or "").strip(),
        "company": str(item.get("organization") or "Unknown").strip(),
        "location": location,
        "skills": skills,
        "description": str(item.get("description_text") or "").strip(),
        "url": apply_url,
        "apply_url": apply_url,
        "job_type": ", ".join(
            value.replace("_", " ").title() for value in employment_types
        ),
        "workplace_type": arrangement,
        "salary": salary,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_currency": str(item.get("ai_salary_currency") or "").strip(),
        "visa_sponsorship": item.get("ai_visa_sponsorship"),
        "location_restrictions": _strings(
            item.get("ai_remote_location_derived")
            or item.get("ai_remote_location")
            or item.get("location_requirements")
        ),
        "updated": item.get("date_posted") or item.get("date_created") or "",
        "expires_at": item.get("date_valid_through") or "",
    }


def _location(item: dict[str, Any], arrangement: str) -> str:
    locations = _strings(
        item.get("locations_derived")
        or item.get("locations_alt")
        or item.get("countries_derived")
    )
    if arrangement.casefold().startswith("remote"):
        if not locations:
            return "Remote"
        if all("remote" not in value.casefold() for value in locations):
            return f"Remote · {', '.join(locations)}"
    return ", ".join(locations)


def _salary(
    item: dict[str, Any],
) -> tuple[str, float | None, float | None]:
    currency = str(item.get("ai_salary_currency") or "").strip()
    unit = str(item.get("ai_salary_unit_text") or "").strip()
    minimum = _number(item.get("ai_salary_min_value"))
    maximum = _number(item.get("ai_salary_max_value"))
    single = _number(item.get("ai_salary_value"))
    if minimum is None and maximum is None and single is not None:
        minimum = maximum = single

    displayed = ""
    if minimum is not None and maximum is not None:
        displayed = f"{currency} {minimum:,.0f} - {maximum:,.0f} {unit}".strip()
    elif minimum is not None:
        displayed = f"{currency} {minimum:,.0f}+ {unit}".strip()
    elif maximum is not None:
        displayed = f"Up to {currency} {maximum:,.0f} {unit}".strip()

    if unit.casefold() != "year":
        return displayed, None, None
    return displayed, minimum, maximum


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        values = value
    elif value is None or value == "":
        return []
    else:
        values = [value]
    return [
        str(item).strip()
        for item in values
        if isinstance(item, (str, int, float)) and str(item).strip()
    ]


def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
