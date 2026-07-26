import math
from concurrent.futures import ThreadPoolExecutor

import requests

from backend.core.settings import (
    ADZUNA_APP_ID,
    ADZUNA_APP_KEY,
    ADZUNA_WORLDWIDE_MARKETS,
)


SUPPORTED_MARKETS = {
    "at", "au", "be", "br", "ca", "ch", "de", "es", "fr", "gb",
    "in", "it", "mx", "nl", "nz", "pl", "sg", "us", "za",
}
COUNTRY_MARKETS = {
    "australia": "au",
    "austria": "at",
    "belgium": "be",
    "brazil": "br",
    "canada": "ca",
    "france": "fr",
    "germany": "de",
    "india": "in",
    "italy": "it",
    "mexico": "mx",
    "netherlands": "nl",
    "new zealand": "nz",
    "poland": "pl",
    "singapore": "sg",
    "south africa": "za",
    "spain": "es",
    "switzerland": "ch",
    "united kingdom": "gb",
    "uk": "gb",
    "united states": "us",
    "united states of america": "us",
    "usa": "us",
}


def search_jobs(keyword, location="Worldwide", results=50):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    worldwide = location.strip().casefold() == "worldwide"
    markets = _worldwide_markets() if worldwide else [_market_for(location)]
    per_market = max(1, math.ceil(max(1, results) / len(markets)))

    def fetch(market):
        return _search_market(
            market,
            keyword,
            "" if worldwide else location,
            per_market if worldwide else results,
        )

    if len(markets) == 1:
        batches = [fetch(markets[0])]
    else:
        def fetch_available(market):
            try:
                return fetch(market), None
            except RuntimeError as error:
                return [], error

        with ThreadPoolExecutor(max_workers=len(markets)) as executor:
            outcomes = list(executor.map(fetch_available, markets))
        if all(error is not None for _, error in outcomes):
            raise RuntimeError("Adzuna request failed.")
        batches = [batch for batch, _error in outcomes]

    jobs = []
    seen = set()
    for index in range(max(map(len, batches), default=0)):
        for batch in batches:
            if index >= len(batch):
                continue
            job = batch[index]
            key = (
                str(job.get("title") or "").casefold(),
                str(job.get("company") or "").casefold(),
                str(job.get("location") or "").casefold(),
            )
            if key not in seen:
                jobs.append(job)
                seen.add(key)
            if len(jobs) >= results:
                return jobs
    return jobs


def _search_market(market, keyword, location, results):
    url = f"https://api.adzuna.com/v1/api/jobs/{market}/search/1"
    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "results_per_page": results,
        "what": keyword,
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError, AttributeError):
        raise RuntimeError("Adzuna request failed.") from None

    return [
        {
            "title": job.get("title"),
            "company": job.get("company", {}).get("display_name", "Unknown"),
            "location": job.get("location", {}).get("display_name", "Unknown"),
            "skills": [],
            "description": job.get("description", ""),
            "redirect_url": job.get("redirect_url", ""),
            "job_type": job.get("contract_type") or "",
            "salary_min": job.get("salary_min"),
            "salary_max": job.get("salary_max"),
            "updated": job.get("created"),
        }
        for job in data.get("results", [])
        if isinstance(job, dict)
    ]


def _worldwide_markets():
    markets = [
        market for market in ADZUNA_WORLDWIDE_MARKETS
        if market in SUPPORTED_MARKETS
    ]
    return list(dict.fromkeys(markets)) or ["us"]


def _market_for(location):
    normalized = location.strip().casefold()
    for country, market in COUNTRY_MARKETS.items():
        if country in normalized:
            return market
    return _worldwide_markets()[0]


if __name__ == "__main__":

    keyword = input("Job title: ")

    jobs = search_jobs(keyword)

    print(f"\nFound {len(jobs)} jobs\n")

    for index, job in enumerate(jobs, start=1):

        print("=" * 60)
        print(f"{index}. {job['title']}")
        print(f"Company: {job['company']}")
        print(f"Location: {job['location']}")
        print(job["redirect_url"])
