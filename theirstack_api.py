import re
from typing import Any

import requests

from backend.core.settings import THEIRSTACK_API_KEY
from job_search_terms import expand_job_titles


THEIRSTACK_SEARCH_URL = "https://api.theirstack.com/v1/jobs/search"
FREE_PLAN_PAGE_LIMIT = 25
DEFAULT_POSTED_WITHIN_DAYS = 30
COUNTRY_CODES = {
    "australia": "AU",
    "brazil": "BR",
    "canada": "CA",
    "china": "CN",
    "france": "FR",
    "germany": "DE",
    "india": "IN",
    "italy": "IT",
    "japan": "JP",
    "mexico": "MX",
    "netherlands": "NL",
    "new zealand": "NZ",
    "singapore": "SG",
    "south africa": "ZA",
    "spain": "ES",
    "united arab emirates": "AE",
    "united kingdom": "GB",
    "uk": "GB",
    "united states": "US",
    "united states of america": "US",
    "usa": "US",
}


def search_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    if not THEIRSTACK_API_KEY:
        return []

    payload: dict[str, Any] = {
        "job_title_or": expand_job_titles(keyword),
        "limit": max(1, min(FREE_PLAN_PAGE_LIMIT, results)),
        "page": max(1, page) - 1,
        "is_closed": False,
        "posted_at_max_age_days": DEFAULT_POSTED_WITHIN_DAYS,
    }
    _add_location_filters(payload, location)

    try:
        response = requests.post(
            THEIRSTACK_SEARCH_URL,
            headers={
                "Authorization": f"Bearer {THEIRSTACK_API_KEY}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError("Worldwide job index request failed.") from None

    jobs = []
    for job in data.get("data") or []:
        if not isinstance(job, dict):
            continue
        employment = job.get("employment_statuses") or []
        jobs.append({
            "title": job.get("job_title") or job.get("normalized_title") or "",
            "company": job.get("company") or "Unknown",
            "location": (
                job.get("short_location")
                or job.get("long_location")
                or job.get("location")
                or "Worldwide"
            ),
            "skills": job.get("technology_slugs") or [],
            "description": job.get("description") or "",
            "url": (
                job.get("final_url")
                or job.get("url")
                or job.get("source_url")
                or ""
            ),
            "job_type": ", ".join(
                str(value).replace("_", " ").title()
                for value in employment
            ),
            "salary": job.get("salary_string") or "",
            "salary_min": job.get("min_annual_salary_usd"),
            "salary_max": job.get("max_annual_salary_usd"),
            "updated": job.get("date_posted") or job.get("discovered_at") or "",
        })
    return jobs


def _add_location_filters(payload: dict[str, Any], location: str) -> None:
    normalized = str(location or "").strip()
    if not normalized or normalized.casefold() == "worldwide":
        return
    if normalized.casefold() == "remote":
        payload["remote"] = True
        return

    parts = [part.strip() for part in normalized.split(",") if part.strip()]
    country_code = COUNTRY_CODES.get(parts[-1].casefold()) if parts else None
    if country_code:
        payload["job_country_code_or"] = [country_code]
    if len(parts) > 1:
        payload["job_location_pattern_or"] = [re.escape(parts[0])]
    elif not country_code:
        payload["job_location_pattern_or"] = [re.escape(normalized)]
