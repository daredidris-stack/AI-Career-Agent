import re


ROLE_ALIASES = {
    "data center technician": (
        "data center technician",
        "datacenter technician",
        "data centre technician",
        "critical facilities technician",
        "critical environment technician",
        "data center operations technician",
        "infrastructure technician",
    ),
    "datacenter technician": (
        "data center technician",
        "datacenter technician",
        "data centre technician",
        "critical facilities technician",
        "critical environment technician",
        "data center operations technician",
        "infrastructure technician",
    ),
    "site reliability engineer": (
        "site reliability engineer",
        "sre",
        "reliability engineer",
        "production engineer",
        "platform reliability engineer",
    ),
}


def expand_job_titles(keyword: str) -> list[str]:
    """Return search-ready title variants without losing the user's wording."""
    value = " ".join(str(keyword or "").split())
    if not value:
        return []

    normalized = _normalize(value)
    aliases = ROLE_ALIASES.get(normalized, ())
    values = [value, *aliases]
    unique = []
    seen = set()
    for item in values:
        key = _normalize(item)
        if key and key not in seen:
            unique.append(item)
            seen.add(key)
    return unique


def title_matches(title: str, keyword: str) -> bool:
    """Match titles against known role aliases using whole normalized terms."""
    normalized_title = _normalize(title)
    if not normalized_title:
        return False
    return any(
        all(
            term in normalized_title.split()
            for term in _normalize(alias).split()
        )
        for alias in expand_job_titles(keyword)
    )


def _normalize(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", str(value or "").casefold()))
