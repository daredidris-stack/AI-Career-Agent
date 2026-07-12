import requests

from config import ADZUNA_APP_ID, ADZUNA_APP_KEY


def search_jobs(keyword, location="Mexico", results=10):

    url = (
        f"https://api.adzuna.com/v1/api/jobs/mx/search/1"
        f"?app_id={ADZUNA_APP_ID}"
        f"&app_key={ADZUNA_APP_KEY}"
        f"&results_per_page={results}"
        f"&what={keyword}"
        f"&where={location}"
        f"&content-type=application/json"
    )

    response = requests.get(url)

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
            "redirect_url": job.get("redirect_url", "")
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