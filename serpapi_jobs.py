import re
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Any

import requests

from backend.core.settings import SERPAPI_API_KEY


SERPAPI_SEARCH_URL = "https://serpapi.com/search.json"
_PAGE_TOKENS: dict[tuple[str, str, int], str] = {}
_PAGE_TOKEN_LOCK = Lock()


def search_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    del results  # Google Jobs currently returns at most ten jobs per page.
    if not SERPAPI_API_KEY:
        return []

    page = max(1, page)
    normalized_location = str(location or "").strip()
    query = keyword
    params: dict[str, Any] = {
        "engine": "google_jobs",
        "q": query,
        "hl": "en",
        "output": "json",
        "api_key": SERPAPI_API_KEY,
    }
    if normalized_location.casefold() == "remote":
        params["q"] = f"{keyword} remote"
    elif normalized_location.casefold() not in {"", "worldwide"}:
        params["location"] = normalized_location

    cache_key = (
        str(params["q"]).strip().casefold(),
        normalized_location.casefold(),
    )
    if page > 1:
        with _PAGE_TOKEN_LOCK:
            next_page_token = _PAGE_TOKENS.get((*cache_key, page))
        if not next_page_token:
            return []
        params["next_page_token"] = next_page_token

    try:
        response = requests.get(
            SERPAPI_SEARCH_URL,
            params=params,
            timeout=20,
        )
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError("Google Jobs index request failed.") from None

    api_error = str(data.get("error") or "")
    if "hasn't returned any results" in api_error.casefold():
        return []
    if api_error:
        raise RuntimeError("Google Jobs index request failed.")

    pagination = data.get("serpapi_pagination") or {}
    if not isinstance(pagination, dict):
        pagination = {}
    next_page_token = pagination.get("next_page_token")
    if next_page_token:
        with _PAGE_TOKEN_LOCK:
            _PAGE_TOKENS[(*cache_key, page + 1)] = str(next_page_token)

    jobs = []
    for item in data.get("jobs_results") or []:
        if not isinstance(item, dict):
            continue
        detected = item.get("detected_extensions") or {}
        if not isinstance(detected, dict):
            detected = {}
        apply_url = _apply_url(item)
        job_type = str(detected.get("schedule_type") or "")
        if detected.get("work_from_home") and "remote" not in job_type.casefold():
            job_type = ", ".join(filter(None, (job_type, "Remote")))
        jobs.append({
            "source_job_id": str(item.get("job_id") or ""),
            "title": item.get("title") or "",
            "company": item.get("company_name") or "Unknown",
            "location": item.get("location") or "Worldwide",
            "skills": [],
            "description": item.get("description") or "",
            "url": apply_url,
            "apply_url": apply_url,
            "job_type": job_type,
            "salary": detected.get("salary") or "",
            "updated": _posted_at(detected.get("posted_at")),
        })
    return jobs


def _apply_url(item: dict[str, Any]) -> str:
    for option in item.get("apply_options") or []:
        if isinstance(option, dict) and option.get("link"):
            return str(option["link"])
    return str(item.get("share_link") or "")


def _posted_at(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    normalized = text.casefold()
    now = datetime.now(timezone.utc)
    if normalized in {"today", "just posted", "just now"}:
        return now.isoformat()

    match = re.search(
        r"(\d+)\s+(minute|hour|day|week|month)s?\s+ago",
        normalized,
    )
    if not match:
        return text
    count = int(match.group(1))
    unit = match.group(2)
    if unit == "minute":
        delta = timedelta(minutes=count)
    elif unit == "hour":
        delta = timedelta(hours=count)
    elif unit == "day":
        delta = timedelta(days=count)
    elif unit == "week":
        delta = timedelta(weeks=count)
    else:
        delta = timedelta(days=count * 30)
    return (now - delta).isoformat()
