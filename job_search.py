import requests


ROLE_ALIASES = {
    "sre": ("site reliability", "reliability engineer", "platform engineer"),
    "site reliability engineer": (
        "site reliability",
        "reliability engineer",
        "sre",
        "platform engineer",
        "devops engineer",
        "infrastructure engineer",
    ),
}


def search_jobs(keyword):

    url = "https://remoteok.com/api"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    jobs = response.json()

    results = []

    for job in jobs[1:]:

        title = job.get("position", "")

        if _matches_title(title, keyword):

            results.append({
                "title": title,
                "company": job.get("company", ""),
                "location": "Remote",
                "url": job.get("url", ""),
                "job_type": job.get("job_type") or "",
                "salary_min": job.get("salary_min"),
                "salary_max": job.get("salary_max"),
                "updated": job.get("date"),
            })

    return results


def _matches_title(title, keyword):
    normalized_title = str(title or "").casefold()
    normalized_keyword = str(keyword or "").strip().casefold()
    aliases = ROLE_ALIASES.get(normalized_keyword, ())
    if normalized_keyword in normalized_title or any(
        alias in normalized_title for alias in aliases
    ):
        return True

    terms = [term for term in normalized_keyword.split() if len(term) > 2]
    required_matches = max(1, round(len(terms) * 0.6))
    return bool(terms) and sum(term in normalized_title for term in terms) >= required_matches


if __name__ == "__main__":

    keyword = input("Job title: ")

    jobs = search_jobs(keyword)

    print()

    for job in jobs:

        print(job["title"])
        print(job["company"])
        print(job["location"])
        print(job["url"])
        print("-" * 40)
