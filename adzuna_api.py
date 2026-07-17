import requests

from backend.core.settings import ADZUNA_APP_ID, ADZUNA_APP_KEY


def search_jobs(keyword, location="Mexico", results=10):

    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        return []

    url = "https://api.adzuna.com/v1/api/jobs/mx/search/1"

    response = requests.get(
        url,
        params={
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": results,
            "what": keyword,
            "where": location,
            "content-type": "application/json",
        },
        timeout=15,
    )

    if response.status_code != 200:
        print("Error:", response.status_code)
        print(response.text)
        return []

    data = response.json()

    jobs = []

    for job in data.get("results", []):

        jobs.append({
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
})

    return jobs


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
