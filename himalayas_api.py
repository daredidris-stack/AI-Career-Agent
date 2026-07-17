import re
from typing import Any

import requests


API_URL = "https://himalayas.app/jobs/api/search"


def search_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
) -> list[dict[str, Any]]:
    params: dict[str, Any] = {
        "q": keyword,
        "page": max(1, page),
        "sort": "relevant",
    }
    country = _country_filter(location)
    if country:
        params["country"] = country
    elif location.strip().casefold() == "worldwide":
        params["worldwide"] = True

    response = requests.get(API_URL, params=params, timeout=15)
    response.raise_for_status()

    return [_normalize(job) for job in response.json().get("jobs", [])]


def _country_filter(location: str) -> str:
    normalized = location.strip()
    if normalized.casefold() in {"", "remote", "worldwide"}:
        return ""
    return normalized.rsplit(",", maxsplit=1)[-1].strip()


def _normalize(job: dict[str, Any]) -> dict[str, Any]:
    locations = job.get("locationRestrictions") or []
    location = ", ".join(
        item.get("name", "") for item in locations if item.get("name")
    ) or "Worldwide remote"
    salary = _salary(job)

    return {
        "title": job.get("title") or "",
        "company": job.get("companyName") or "",
        "location": location,
        "description": _plain_text(
            job.get("description") or job.get("excerpt") or ""
        ),
        "skills": job.get("categories") or [],
        "url": job.get("applicationLink") or "",
        "job_type": job.get("employmentType") or "",
        "salary": salary,
        "salary_min": job.get("minSalary"),
        "salary_max": job.get("maxSalary"),
        "updated": job.get("pubDate"),
    }


def _salary(job: dict[str, Any]) -> str:
    minimum = job.get("minSalary")
    maximum = job.get("maxSalary")
    if minimum is None and maximum is None:
        return ""

    values = " - ".join(
        f"{value:,.0f}" for value in (minimum, maximum) if value is not None
    )
    return " ".join(filter(None, [
        job.get("currency"),
        values,
        f"per {job.get('salaryPeriod', 'annual')}",
    ]))


def _plain_text(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value).strip()
