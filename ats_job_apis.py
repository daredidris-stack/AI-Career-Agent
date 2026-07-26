import html
import re
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Callable
from urllib.parse import quote

import requests

from backend.core.settings import (
    ASHBY_JOB_BOARDS,
    GREENHOUSE_JOB_BOARDS,
    LEVER_JOB_SITES,
)
from job_search_terms import title_matches


GREENHOUSE_API_ROOT = "https://boards-api.greenhouse.io/v1/boards"
LEVER_API_ROOT = "https://api.lever.co/v0/postings"
ASHBY_API_ROOT = "https://api.ashbyhq.com/posting-api/job-board"
SAFE_BOARD_NAME = re.compile(r"^[A-Za-z0-9_-]+$")


def search_greenhouse_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    return _search_boards(
        GREENHOUSE_JOB_BOARDS,
        lambda company, board: _greenhouse_board(company, board),
        keyword,
        location,
        page,
        results,
        "Greenhouse employer feeds failed.",
    )


def search_lever_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    return _search_boards(
        LEVER_JOB_SITES,
        lambda company, site: _lever_site(company, site),
        keyword,
        location,
        page,
        results,
        "Lever employer feeds failed.",
    )


def search_ashby_jobs(
    keyword: str,
    location: str = "Worldwide",
    page: int = 1,
    results: int = 50,
) -> list[dict[str, Any]]:
    return _search_boards(
        ASHBY_JOB_BOARDS,
        lambda company, board: _ashby_board(company, board),
        keyword,
        location,
        page,
        results,
        "Ashby employer feeds failed.",
    )


def _search_boards(
    configured_boards: list[str],
    fetcher: Callable[[str, str], list[dict[str, Any]]],
    keyword: str,
    location: str,
    page: int,
    results: int,
    error_message: str,
) -> list[dict[str, Any]]:
    boards = _board_specs(configured_boards)
    if not boards:
        return []

    def fetch(spec: tuple[str, str]):
        try:
            return fetcher(*spec), None
        except RuntimeError as error:
            return [], error

    with ThreadPoolExecutor(max_workers=min(8, len(boards))) as executor:
        outcomes = list(executor.map(fetch, boards))

    if outcomes and all(error is not None for _jobs, error in outcomes):
        raise RuntimeError(error_message)

    batches = [
        [
            job for job in jobs
            if title_matches(job.get("title") or "", keyword)
            and _matches_location(job, location)
        ]
        for jobs, _error in outcomes
    ]
    blended = _blend(batches)
    page_size = max(1, results)
    start = (max(1, page) - 1) * page_size
    return blended[start:start + page_size]


def _greenhouse_board(company: str, board: str) -> list[dict[str, Any]]:
    data = _get_json(
        f"{GREENHOUSE_API_ROOT}/{quote(board)}/jobs",
        params={"content": "true"},
    )
    if not isinstance(data, dict):
        raise RuntimeError("Greenhouse employer feed returned invalid data.")

    jobs = []
    for item in data.get("jobs") or []:
        if not isinstance(item, dict):
            continue
        job_location = item.get("location") or {}
        url = str(item.get("absolute_url") or "").strip()
        jobs.append({
            "source_job_id": str(item.get("id") or ""),
            "title": item.get("title") or "",
            "company": company,
            "location": (
                job_location.get("name")
                if isinstance(job_location, dict) else str(job_location)
            ) or "",
            "skills": [],
            "description": _plain_text(item.get("content")),
            "url": url,
            "apply_url": url,
            "job_type": "",
            "updated": item.get("updated_at") or "",
        })
    return jobs


def _lever_site(company: str, site: str) -> list[dict[str, Any]]:
    data = _get_json(
        f"{LEVER_API_ROOT}/{quote(site)}",
        params={"mode": "json"},
    )
    if not isinstance(data, list):
        raise RuntimeError("Lever employer feed returned invalid data.")

    jobs = []
    for item in data:
        if not isinstance(item, dict):
            continue
        categories = item.get("categories") or {}
        if not isinstance(categories, dict):
            categories = {}
        locations = categories.get("allLocations") or []
        if not isinstance(locations, list):
            locations = [locations]
        location = ", ".join(map(str, locations)) or str(
            categories.get("location") or ""
        )
        description_parts = [
            item.get("descriptionPlain") or item.get("description"),
            *[
                section.get("content")
                for section in item.get("lists") or []
                if isinstance(section, dict)
            ],
            item.get("additionalPlain") or item.get("additional"),
        ]
        hosted_url = str(item.get("hostedUrl") or "").strip()
        apply_url = str(item.get("applyUrl") or "").strip()
        salary, salary_min, salary_max = _lever_salary(item)
        jobs.append({
            "source_job_id": str(item.get("id") or ""),
            "title": item.get("text") or "",
            "company": company,
            "location": location,
            "skills": [],
            "description": _plain_text("\n\n".join(
                str(value) for value in description_parts if value
            )),
            "url": apply_url or hosted_url,
            "apply_url": apply_url or hosted_url,
            "job_type": categories.get("commitment") or "",
            "workplace_type": item.get("workplaceType") or "",
            "salary": salary,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "updated": "",
        })
    return jobs


def _ashby_board(company: str, board: str) -> list[dict[str, Any]]:
    data = _get_json(
        f"{ASHBY_API_ROOT}/{quote(board)}",
        params={"includeCompensation": "true"},
    )
    if not isinstance(data, dict):
        raise RuntimeError("Ashby employer feed returned invalid data.")

    jobs = []
    for item in data.get("jobs") or []:
        if not isinstance(item, dict) or item.get("isListed") is False:
            continue
        job_url = str(item.get("jobUrl") or "").strip()
        apply_url = str(item.get("applyUrl") or "").strip()
        salary, salary_min, salary_max = _ashby_salary(item)
        jobs.append({
            "source_job_id": job_url.rstrip("/").rsplit("/", 1)[-1],
            "title": item.get("title") or "",
            "company": company,
            "location": item.get("location") or "",
            "skills": [],
            "description": _plain_text(
                item.get("descriptionPlain") or item.get("descriptionHtml")
            ),
            "url": apply_url or job_url,
            "apply_url": apply_url or job_url,
            "job_type": _split_camel_case(item.get("employmentType")),
            "workplace_type": item.get("workplaceType") or "",
            "salary": salary,
            "salary_min": salary_min,
            "salary_max": salary_max,
            "updated": item.get("publishedAt") or "",
        })
    return jobs


def _get_json(url: str, params: dict[str, Any]) -> Any:
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError("Employer job feed request failed.") from None


def _board_specs(values: list[str]) -> list[tuple[str, str]]:
    specs = []
    seen = set()
    for value in values:
        parts = [part.strip() for part in str(value).split("|", 1)]
        board = parts[-1]
        if not SAFE_BOARD_NAME.fullmatch(board) or board.casefold() in seen:
            continue
        company = (
            parts[0] if len(parts) == 2 and parts[0]
            else board.replace("-", " ").replace("_", " ").title()
        )
        specs.append((company, board))
        seen.add(board.casefold())
    return specs


def _matches_location(job: dict[str, Any], requested: str) -> bool:
    expected = str(requested or "").strip().casefold()
    if expected in {"", "worldwide"}:
        return True
    workplace = str(job.get("workplace_type") or "").casefold()
    location = str(job.get("location") or "").casefold()
    if expected == "remote":
        return "remote" in workplace or "remote" in location
    return all(
        part.strip() in location
        for part in expected.split(",")
        if part.strip()
    )


def _blend(batches: list[list[dict[str, Any]]]) -> list[dict[str, Any]]:
    blended = []
    for index in range(max(map(len, batches), default=0)):
        for batch in batches:
            if index < len(batch):
                blended.append(batch[index])
    return blended


def _lever_salary(item: dict[str, Any]) -> tuple[str, float | None, float | None]:
    salary_range = item.get("salaryRange") or {}
    if not isinstance(salary_range, dict):
        salary_range = {}
    description = _plain_text(
        item.get("salaryDescriptionPlain")
        or item.get("salaryDescription")
    )
    interval = str(salary_range.get("interval") or "").casefold()
    annual = interval in {"year", "yearly", "annual", "annually"}
    return (
        description,
        _number(salary_range.get("min")) if annual else None,
        _number(salary_range.get("max")) if annual else None,
    )


def _ashby_salary(item: dict[str, Any]) -> tuple[str, float | None, float | None]:
    compensation = item.get("compensation") or {}
    if not isinstance(compensation, dict):
        compensation = {}
    summary = str(
        compensation.get("scrapeableCompensationSalarySummary")
        or compensation.get("compensationTierSummary")
        or ""
    )
    for component in compensation.get("summaryComponents") or []:
        if not isinstance(component, dict):
            continue
        if (
            str(component.get("compensationType") or "").casefold() == "salary"
            and str(component.get("interval") or "").casefold()
            in {"1 year", "year", "yearly", "annual"}
        ):
            return (
                summary,
                _number(component.get("minValue")),
                _number(component.get("maxValue")),
            )
    return summary, None, None


def _number(value: Any) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def _split_camel_case(value: Any) -> str:
    return re.sub(r"(?<=[a-z])(?=[A-Z])", " ", str(value or "")).strip()


def _plain_text(value: Any) -> str:
    text = html.unescape(html.unescape(str(value or "")))
    text = re.sub(r"<\s*br\s*/?\s*>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(
        r"</\s*(?:div|h[1-6]|li|ol|p|section|ul)\s*>",
        "\n",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"<[^>]+>", " ", text)
    lines = [" ".join(line.split()) for line in text.splitlines()]
    return "\n".join(line for line in lines if line).strip()
