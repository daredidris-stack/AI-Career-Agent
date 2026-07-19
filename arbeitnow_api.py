import re
from typing import Any

import requests


API_URL = "https://www.arbeitnow.com/api/job-board-api"
ROLE_ALIASES = {
    "sre": (
        "site reliability",
        "reliability engineer",
        "devops engineer",
        "platform engineer",
    ),
    "site reliability engineer": (
        "site reliability",
        "reliability engineer",
        "sre",
        "platform engineer",
        "devops engineer",
        "infrastructure engineer",
    ),
}


def search_jobs(
    keyword: str,
    location: str = "Worldwide",
    industry: str = "",
    results: int = 10,
) -> list[dict[str, Any]]:
    response = requests.get(API_URL, timeout=15)
    response.raise_for_status()
    jobs = response.json().get("data", [])
    matches = []

    for job in jobs:
        if not _matches_keyword(job, keyword):
            continue
        if industry and not _contains(job, industry):
            continue
        if not _matches_location(job, location):
            continue

        matches.append({
            "title": job.get("title") or "",
            "company": job.get("company_name") or "",
            "location": job.get("location") or (
                "Remote" if job.get("remote") else ""
            ),
            "description": _plain_text(job.get("description") or ""),
            "skills": job.get("tags") or [],
            "url": job.get("url") or "",
            "job_type": "Full Time" if job.get("job_types") == ["full_time"] else "",
            "updated": job.get("created_at"),
        })

        if len(matches) >= results:
            break

    return matches


def _matches_keyword(job: dict[str, Any], keyword: str) -> bool:
    normalized_keyword = keyword.strip().casefold()
    aliases = ROLE_ALIASES.get(normalized_keyword, (normalized_keyword,))
    title = str(job.get("title") or "").casefold()
    if any(alias in title for alias in aliases):
        return True

    terms = [term for term in normalized_keyword.split() if len(term) > 2]
    required_matches = max(1, round(len(terms) * 0.6))
    return bool(terms) and sum(term in title for term in terms) >= required_matches


def _matches_location(job: dict[str, Any], location: str) -> bool:
    normalized_location = location.strip().casefold()
    if normalized_location in {"", "worldwide"}:
        return True
    if normalized_location == "remote":
        return bool(job.get("remote"))
    return normalized_location in str(job.get("location") or "").casefold()


def _contains(job: dict[str, Any], value: str) -> bool:
    searchable = " ".join([
        str(job.get("title") or ""),
        str(job.get("description") or ""),
        " ".join(str(tag) for tag in job.get("tags") or []),
    ]).casefold()
    return value.casefold() in searchable


def _plain_text(value: str) -> str:
    return re.sub(r"<[^>]+>", " ", value).strip()
