import html
import json
import re
from difflib import SequenceMatcher
from html.parser import HTMLParser
from typing import Any
from urllib.parse import quote, urlparse

import requests


AMAZON_SEARCH_URL = "https://www.amazon.jobs/en/search.json"
GREENHOUSE_API_ROOT = "https://boards-api.greenhouse.io/v1/boards"
LEVER_API_ROOT = "https://api.lever.co/v0/postings"
ASHBY_API_ROOT = "https://api.ashbyhq.com/posting-api/job-board"
MICROSOFT_DETAIL_URL = (
    "https://apply.careers.microsoft.com/api/pcsx/position_details"
)
SAFE_SLUG = re.compile(r"^[A-Za-z0-9_-]+$")


class JobDescriptionService:
    def enrich(
        self,
        title: str,
        company: str = "",
        location: str = "",
        listing_url: str | None = None,
    ) -> str | None:
        normalized_company = company.casefold()
        if any(
            name in normalized_company
            for name in ("amazon", "amazon web services", "aws")
        ):
            description = self._amazon_description(title, location)
            if description:
                return description

        if listing_url:
            for resolver in (
                self._microsoft_description,
                self._apple_description,
                self._crossover_description,
                self._greenhouse_description,
                self._lever_description,
                self._ashby_description,
            ):
                description = resolver(listing_url)
                if description:
                    return description
        return None

    def _amazon_description(self, title: str, location: str) -> str | None:
        try:
            response = requests.get(
                AMAZON_SEARCH_URL,
                params={
                    "base_query": title,
                    "loc_query": location,
                    "result_limit": 10,
                    "offset": 0,
                },
                timeout=10,
            )
            response.raise_for_status()
            jobs = response.json().get("jobs", [])
        except (requests.RequestException, ValueError, AttributeError):
            return None

        job = _best_job_match(jobs, title, location)
        if not job:
            return None
        return _join_sections(
            ("", job.get("description")),
            ("Basic qualifications", job.get("basic_qualifications")),
            ("Preferred qualifications", job.get("preferred_qualifications")),
        )

    def _microsoft_description(self, listing_url: str) -> str | None:
        parsed = urlparse(listing_url)
        if (
            not _safe_https_url(parsed)
            or parsed.hostname != "apply.careers.microsoft.com"
        ):
            return None
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 3 or parts[-2] != "job" or not parts[-1].isdigit():
            return None

        data = _get_json(
            MICROSOFT_DETAIL_URL,
            params={
                "position_id": parts[-1],
                "domain": "microsoft.com",
                "hl": "en",
            },
        )
        details = data.get("data") if data else None
        return _plain_text(
            details.get("jobDescription")
            if isinstance(details, dict) else None
        ) or None

    def _apple_description(self, listing_url: str) -> str | None:
        parsed = urlparse(listing_url)
        if (
            not _safe_https_url(parsed)
            or parsed.hostname != "jobs.apple.com"
            or "/details/" not in parsed.path
        ):
            return None
        page = _get_text(listing_url)
        if not page:
            return None

        match = re.search(
            r"window\.__staticRouterHydrationData\s*=\s*"
            r"JSON\.parse\((\"(?:\\.|[^\"\\])*\")\)",
            page,
            re.DOTALL,
        )
        if not match:
            return None
        try:
            payload = json.loads(json.loads(match.group(1)))
            details = payload["loaderData"]["jobDetails"]["jobsData"]
        except (json.JSONDecodeError, KeyError, TypeError):
            return None

        return _join_sections(
            ("Summary", details.get("jobSummary")),
            ("Description", details.get("description")),
            ("Minimum qualifications", details.get("minimumQualifications")),
            (
                "Preferred qualifications",
                details.get("preferredQualifications"),
            ),
        )

    def _crossover_description(self, listing_url: str) -> str | None:
        parsed = urlparse(listing_url)
        if (
            not _safe_https_url(parsed)
            or parsed.hostname
            not in {"www.crossover.com", "ed.crossover.com"}
        ):
            return None
        page = _get_text(listing_url)
        if not page:
            return None
        parser = _JsonLdExtractor()
        parser.feed(page)
        for raw in parser.values:
            try:
                payload = json.loads(raw)
            except (json.JSONDecodeError, TypeError):
                continue
            for item in _json_ld_items(payload):
                if item.get("@type") == "JobPosting":
                    return _plain_text(item.get("description")) or None
        return None

    def _greenhouse_description(self, listing_url: str) -> str | None:
        parsed = urlparse(listing_url)
        if not _safe_https_url(parsed) or parsed.hostname not in {
            "boards.greenhouse.io",
            "job-boards.greenhouse.io",
        }:
            return None
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 3 or parts[-2] != "jobs":
            return None
        board, job_id = parts[0], parts[-1]
        if not SAFE_SLUG.fullmatch(board) or not job_id.isdigit():
            return None

        data = _get_json(
            f"{GREENHOUSE_API_ROOT}/{quote(board)}/jobs/{job_id}"
        )
        return _plain_text(data.get("content")) if data else None

    def _lever_description(self, listing_url: str) -> str | None:
        parsed = urlparse(listing_url)
        if not _safe_https_url(parsed) or parsed.hostname != "jobs.lever.co":
            return None
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            return None
        site, posting_id = parts[0], parts[1]
        if not SAFE_SLUG.fullmatch(site) or not SAFE_SLUG.fullmatch(posting_id):
            return None

        data = _get_json(
            f"{LEVER_API_ROOT}/{quote(site)}/{quote(posting_id)}"
        )
        if not data:
            return None
        list_sections = [
            (str(item.get("text") or ""), item.get("content"))
            for item in data.get("lists", [])
            if isinstance(item, dict)
        ]
        return _join_sections(
            ("", data.get("openingPlain") or data.get("opening")),
            ("", data.get("descriptionPlain") or data.get("description")),
            *list_sections,
            ("", data.get("additionalPlain") or data.get("additional")),
        )

    def _ashby_description(self, listing_url: str) -> str | None:
        parsed = urlparse(listing_url)
        if (
            not _safe_https_url(parsed)
            or parsed.hostname != "jobs.ashbyhq.com"
        ):
            return None
        parts = [part for part in parsed.path.split("/") if part]
        if len(parts) < 2:
            return None
        board, posting_id = parts[0], parts[1]
        if not SAFE_SLUG.fullmatch(board) or not SAFE_SLUG.fullmatch(posting_id):
            return None

        data = _get_json(f"{ASHBY_API_ROOT}/{quote(board)}")
        if not data:
            return None
        for job in data.get("jobs", []):
            if not isinstance(job, dict):
                continue
            job_url = str(job.get("jobUrl") or "")
            if urlparse(job_url).path.rstrip("/").endswith(f"/{posting_id}"):
                return _plain_text(
                    job.get("descriptionPlain")
                    or job.get("descriptionHtml")
                )
        return None


def _get_json(
    url: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None
    return data if isinstance(data, dict) else None


def _get_text(url: str) -> str | None:
    try:
        response = requests.get(url, timeout=10, allow_redirects=False)
        response.raise_for_status()
    except requests.RequestException:
        return None
    return response.text


def _safe_https_url(parsed) -> bool:
    try:
        port = parsed.port
    except ValueError:
        return False
    return (
        parsed.scheme == "https"
        and parsed.hostname is not None
        and parsed.username is None
        and parsed.password is None
        and port in {None, 443}
    )


def _json_ld_items(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    if not isinstance(value, dict):
        return []
    graph = value.get("@graph")
    if isinstance(graph, list):
        return [item for item in graph if isinstance(item, dict)]
    return [value]


def _best_job_match(
    jobs: Any,
    expected_title: str,
    expected_location: str,
) -> dict[str, Any] | None:
    if not isinstance(jobs, list):
        return None
    normalized_title = _normalized(expected_title)
    normalized_location = _normalized(expected_location)
    best_job = None
    best_score = 0.0

    for job in jobs:
        if not isinstance(job, dict):
            continue
        title_score = SequenceMatcher(
            None,
            normalized_title,
            _normalized(job.get("title")),
        ).ratio()
        location_score = SequenceMatcher(
            None,
            normalized_location,
            _normalized(job.get("location")),
        ).ratio() if normalized_location else 1.0
        score = (title_score * 0.85) + (location_score * 0.15)
        if score > best_score:
            best_job = job
            best_score = score

    return best_job if best_score >= 0.68 else None


def _normalized(value: Any) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))


def _join_sections(*sections: tuple[str, Any]) -> str | None:
    values = []
    for heading, content in sections:
        text = _plain_text(content)
        if not text:
            continue
        values.append(f"{heading}\n{text}" if heading else text)
    return "\n\n".join(values) or None


class _TextExtractor(HTMLParser):
    BLOCK_TAGS = {
        "br", "div", "h1", "h2", "h3", "h4", "li", "p", "section",
        "ul", "ol",
    }

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, _attrs) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")
        if tag == "li":
            self.parts.append("- ")

    def handle_endtag(self, tag: str) -> None:
        if tag in self.BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        self.parts.append(data)


class _JsonLdExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.capture = False
        self.parts: list[str] = []
        self.values: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        attributes = dict(attrs)
        if tag == "script" and attributes.get("type") == "application/ld+json":
            self.capture = True
            self.parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self.capture:
            self.values.append("".join(self.parts))
            self.capture = False
            self.parts = []

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.parts.append(data)


def _plain_text(value: Any) -> str:
    raw = html.unescape(str(value or "")).strip()
    if not raw:
        return ""
    parser = _TextExtractor()
    parser.feed(raw)
    text = "".join(parser.parts).replace("\xa0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()
