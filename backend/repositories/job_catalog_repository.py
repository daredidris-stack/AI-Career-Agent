import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_JOBS_FILE = PROJECT_ROOT / "jobs.json"


class JobCatalogRepository:
    def __init__(
        self,
        jobs_file: Path = DEFAULT_JOBS_FILE,
    ):
        self.jobs_file = jobs_file

    def list_jobs(self) -> list[dict[str, Any]]:
        if not self.jobs_file.exists():
            return []

        with self.jobs_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            jobs = json.load(file)

        if not isinstance(jobs, list):
            raise ValueError(
                "The job catalog must contain a JSON list."
            )

        return [
            job
            for job in jobs
            if isinstance(job, dict)
        ]
