from datetime import datetime, timezone
from typing import Any

import requests

from job_search_terms import title_matches


MICROSOFT_SEARCH_URL = "https://apply.careers.microsoft.com/api/pcsx/search"
APPLE_SEARCH_URL = "https://jobs.apple.com/api/v1/search"
CROSSOVER_SEARCH_URL = "https://profile-api.crossover.com/pipelines"


def search_microsoft_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    params = {
        "domain": "microsoft.com",
        "query": keyword,
        "location": "" if _is_worldwide(location) else location,
        "start": (max(1, page) - 1) * 10,
        "sort_by": "relevance",
        "hl": "en",
    }
    data = _get_json(
        MICROSOFT_SEARCH_URL,
        params=params,
        error_message="Microsoft careers request failed.",
    )
    positions = (data.get("data") or {}).get("positions") or []
    jobs = []
    for position in positions[:max(1, results)]:
        if not isinstance(position, dict):
            continue
        path = str(position.get("positionUrl") or "").strip()
        listing_url = (
            f"https://apply.careers.microsoft.com{path}?hl=en"
            if path.startswith("/") else path
        )
        locations = position.get("locations") or []
        jobs.append({
            "title": position.get("name") or "",
            "company": "Microsoft",
            "location": ", ".join(map(str, locations)) or "Worldwide",
            "skills": [],
            "description": "",
            "url": listing_url,
            "job_type": _work_mode(position.get("workLocationOption")),
            "updated": position.get("postedTs") or position.get("creationTs"),
        })
    return jobs


def search_apple_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    data = _post_json(
        APPLE_SEARCH_URL,
        payload={
            "query": keyword,
            "filters": {},
            "page": max(1, page),
            "locale": "en-us",
            "sort": "relevance",
            "format": {
                "longDate": "MMMM D, YYYY",
                "mediumDate": "MMM D, YYYY",
            },
        },
        error_message="Apple careers request failed.",
    )
    records = (data.get("res") or {}).get("searchResults") or []
    jobs = []
    for record in records:
        if not isinstance(record, dict) or not _apple_location_matches(
            record, location
        ):
            continue
        locations = record.get("locations") or []
        location_names = [
            ", ".join(filter(None, (
                str(item.get("name") or "").strip(),
                str(item.get("stateProvince") or "").strip(),
                str(item.get("countryName") or "").strip(),
            )))
            for item in locations
            if isinstance(item, dict)
        ]
        job_id = str(record.get("id") or record.get("reqId") or "").strip()
        slug = str(record.get("transformedPostingTitle") or "").strip()
        listing_url = (
            f"https://jobs.apple.com/en-us/details/{job_id}/{slug}"
            if job_id and slug else ""
        )
        jobs.append({
            "title": record.get("postingTitle") or "",
            "company": "Apple",
            "location": "; ".join(filter(None, location_names)) or "Worldwide",
            "skills": [],
            "description": record.get("jobSummary") or "",
            "url": listing_url,
            "job_type": "Remote" if record.get("homeOffice") else "Full time",
            "updated": record.get("postDateInGMT") or "",
        })
        if len(jobs) >= max(1, results):
            break
    return jobs


def search_crossover_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    data = _get_json(
        CROSSOVER_SEARCH_URL,
        params={"status": "Active"},
        error_message="Crossover careers request failed.",
    )
    matching = [
        record for record in data.get("records") or []
        if isinstance(record, dict)
        and title_matches(record.get("Name") or "", keyword)
        and _crossover_location_matches(record, location)
    ]
    start = (max(1, page) - 1) * max(1, results)
    jobs = []
    for record in matching[start:start + max(1, results)]:
        brand = record.get("Brand__r") or {}
        yearly_rate = record.get("Yearly_Rate__c")
        hourly_rate = record.get("Hourly_Rate__c")
        jobs.append({
            "title": record.get("Name") or "",
            "company": brand.get("Name") or "Crossover",
            "location": _crossover_location(record),
            "skills": [],
            "description": "",
            "url": (
                record.get("Landing_Page_URL__c")
                or record.get("DisplayUrl")
                or ""
            ),
            "job_type": str(record.get("Job_Type__c") or "").replace("-", " "),
            "salary": _crossover_salary(hourly_rate, yearly_rate),
            "salary_min": yearly_rate,
            "salary_max": yearly_rate,
            "updated": "",
        })
    return jobs


def _get_json(url: str, params: dict[str, Any], error_message: str) -> dict:
    try:
        response = requests.get(url, params=params, timeout=12)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError(error_message) from None
    return data if isinstance(data, dict) else {}


def _post_json(url: str, payload: dict[str, Any], error_message: str) -> dict:
    try:
        response = requests.post(url, json=payload, timeout=12)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError(error_message) from None
    return data if isinstance(data, dict) else {}


def _is_worldwide(location: str) -> bool:
    return str(location or "").strip().casefold() == "worldwide"


def _work_mode(value: Any) -> str:
    mode = str(value or "").strip().replace("_", " ")
    return mode.title() if mode else ""


def _apple_location_matches(record: dict[str, Any], location: str) -> bool:
    if _is_worldwide(location):
        return True
    if str(location or "").strip().casefold() == "remote":
        return bool(record.get("homeOffice"))
    expected = [
        value.strip().casefold()
        for value in str(location or "").split(",")
        if value.strip()
    ]
    searchable = " ".join(
        " ".join(str(value or "") for value in item.values())
        for item in record.get("locations") or []
        if isinstance(item, dict)
    ).casefold()
    return all(value in searchable for value in expected)


def _crossover_location_matches(record: dict[str, Any], location: str) -> bool:
    if _is_worldwide(location):
        return True
    normalized = str(location or "").strip().casefold()
    if normalized == "remote":
        return not bool(record.get("Is_InPerson__c"))
    return all(
        term.strip() in _crossover_location(record).casefold()
        for term in normalized.split(",")
        if term.strip()
    )


def _crossover_location(record: dict[str, Any]) -> str:
    if str(record.get("Geographic_Restriction__c") or "").casefold() == "global":
        return "Worldwide remote"
    names = []
    work_locations = record.get("Work_Locations__r") or {}
    for item in work_locations.get("records") or []:
        if not isinstance(item, dict):
            continue
        name = item.get("Name") or item.get("City__c")
        if name:
            names.append(str(name))
    country = str(record.get("Work_Country__c") or "").strip()
    if country and country not in names:
        names.append(country)
    return ", ".join(names) or "Remote"


def _crossover_salary(hourly_rate: Any, yearly_rate: Any) -> str:
    if yearly_rate:
        return f"${yearly_rate:,.0f}/year USD"
    if hourly_rate:
        return f"${hourly_rate:,.0f}/hour USD"
    return ""
