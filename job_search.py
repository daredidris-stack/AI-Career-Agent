import requests


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

        if keyword.lower() in title.lower():

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
