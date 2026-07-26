import html
from typing import Any

import requests

from backend.core.settings import USAJOBS_API_KEY, USAJOBS_USER_AGENT


USAJOBS_SEARCH_URL = "https://data.usajobs.gov/api/search"


def search_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    if not USAJOBS_API_KEY or not USAJOBS_USER_AGENT:
        return []

    params: dict[str, Any] = {
        "Keyword": keyword,
        "Page": max(1, page),
        "ResultsPerPage": max(1, min(500, results)),
        "Fields": "Full",
    }
    normalized_location = str(location or "").strip()
    if normalized_location.casefold() == "remote":
        params["RemoteIndicator"] = "True"
    elif normalized_location.casefold() not in {"", "worldwide"}:
        params["LocationName"] = normalized_location

    try:
        response = requests.get(
            USAJOBS_SEARCH_URL,
            headers={
                "Host": "data.usajobs.gov",
                "User-Agent": USAJOBS_USER_AGENT,
                "Authorization-Key": USAJOBS_API_KEY,
            },
            params=params,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError("USAJOBS request failed.") from None

    search_result = data.get("SearchResult") or {}
    jobs = []
    for result in search_result.get("SearchResultItems") or []:
        if not isinstance(result, dict):
            continue
        item = result.get("MatchedObjectDescriptor") or {}
        if not isinstance(item, dict):
            continue
        user_area = item.get("UserArea") or {}
        if not isinstance(user_area, dict):
            user_area = {}
        details = user_area.get("Details") or {}
        if not isinstance(details, dict):
            details = {}
        apply_urls = item.get("ApplyURI") or []
        position_url = str(item.get("PositionURI") or "").strip()
        apply_url = str(apply_urls[0] if apply_urls else position_url).strip()
        salary, salary_min, salary_max = _salary(item)
        jobs.append({
            "source_job_id": str(
                item.get("PositionID") or result.get("MatchedObjectId") or ""
            ),
            "title": item.get("PositionTitle") or "",
            "company": (
                item.get("OrganizationName")
                or item.get("DepartmentName")
                or "U.S. Federal Government"
            ),
            "location": item.get("PositionLocationDisplay") or "",
            "skills": [
                str(category.get("Name"))
                for category in item.get("JobCategory") or []
                if isinstance(category, dict) and category.get("Name")
            ],
            "description": _description(item, details),
            "url": apply_url or position_url,
            "apply_url": apply_url or position_url,
            "job_type": _job_type(item),
            "salary": salary,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "updated": item.get("PublicationStartDate") or "",
        })
    return jobs


def _description(item: dict[str, Any], details: dict[str, Any]) -> str:
    key_requirements = details.get("KeyRequirements") or []
    if isinstance(key_requirements, list):
        requirements = "\n".join(
            f"- {value}" for value in key_requirements if value
        )
    else:
        requirements = str(key_requirements)

    sections = (
        ("Summary", details.get("JobSummary")),
        ("Qualifications", item.get("QualificationSummary")),
        ("Duties", details.get("MajorDuties")),
        ("Requirements", details.get("Requirements") or requirements),
        ("Education", details.get("Education")),
        ("Evaluation", details.get("Evaluations")),
        ("Benefits", details.get("Benefits")),
        ("How to apply", details.get("HowToApply")),
        ("Additional information", details.get("OtherInformation")),
    )
    return "\n\n".join(
        f"{heading}\n{_plain_text(value)}"
        for heading, value in sections
        if _plain_text(value)
    )


def _job_type(item: dict[str, Any]) -> str:
    values = []
    for field in ("PositionSchedule", "PositionOfferingType"):
        for entry in item.get(field) or []:
            if isinstance(entry, dict) and entry.get("Name"):
                values.append(str(entry["Name"]))
    return ", ".join(dict.fromkeys(values))


def _salary(
    item: dict[str, Any],
) -> tuple[str, float | None, float | None]:
    remuneration = item.get("PositionRemuneration") or []
    if not remuneration or not isinstance(remuneration[0], dict):
        return "", None, None
    value = remuneration[0]
    minimum = _number(value.get("MinimumRange"))
    maximum = _number(value.get("MaximumRange"))
    interval = str(value.get("Description") or "").strip()
    annual = (
        str(value.get("RateIntervalCode") or "").casefold() == "pa"
        or "year" in interval.casefold()
    )
    displayed = ""
    if minimum is not None and maximum is not None:
        displayed = f"${minimum:,.0f} - ${maximum:,.0f} {interval}".strip()
    elif minimum is not None:
        displayed = f"${minimum:,.0f}+ {interval}".strip()
    return (
        displayed,
        minimum if annual else None,
        maximum if annual else None,
    )


def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _plain_text(value: Any) -> str:
    return " ".join(html.unescape(str(value or "")).split())
