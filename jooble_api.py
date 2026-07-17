from typing import Any

import requests

from backend.core.settings import JOOBLE_API_KEY


API_URL = "https://jooble.org/api/{api_key}"


def search_jobs(
    keyword: str,
    location: str = "",
    page: int = 1,
    results: int = 20,
) -> list[dict[str, Any]]:
    if not JOOBLE_API_KEY:
        return []

    response = requests.post(
        API_URL.format(api_key=JOOBLE_API_KEY),
        json={
            "keywords": keyword,
            "location": "" if location == "Worldwide" else location,
            "page": page,
            "ResultOnPage": results,
            "companysearch": False,
        },
        timeout=15,
    )
    response.raise_for_status()

    return [
        {
            "title": job.get("title") or "",
            "company": job.get("company") or "",
            "location": job.get("location") or "",
            "description": job.get("snippet") or "",
            "skills": [],
            "url": job.get("link") or "",
            "job_type": job.get("type") or "",
            "salary": job.get("salary") or "",
            "updated": job.get("updated") or "",
        }
        for job in response.json().get("jobs", [])
    ]
