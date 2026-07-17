import json
import tempfile
import unittest
from pathlib import Path

from backend.repositories.job_catalog_repository import (
    JobCatalogRepository,
)


class JobCatalogRepositoryTests(unittest.TestCase):
    def test_reads_valid_job_catalog(self):
        with tempfile.TemporaryDirectory() as directory:
            jobs_file = Path(directory) / "jobs.json"
            jobs_file.write_text(
                json.dumps(
                    [
                        {
                            "title": "Cloud Engineer",
                            "skills": ["AWS"],
                        }
                    ]
                ),
                encoding="utf-8",
            )

            jobs = JobCatalogRepository(
                jobs_file
            ).list_jobs()

        self.assertEqual(jobs[0]["title"], "Cloud Engineer")

    def test_missing_catalog_returns_empty_list(self):
        repository = JobCatalogRepository(
            Path("/definitely/missing/jobs.json")
        )

        self.assertEqual(repository.list_jobs(), [])

    def test_non_list_catalog_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            jobs_file = Path(directory) / "jobs.json"
            jobs_file.write_text(
                '{"title": "Cloud Engineer"}',
                encoding="utf-8",
            )

            with self.assertRaises(ValueError):
                JobCatalogRepository(jobs_file).list_jobs()


if __name__ == "__main__":
    unittest.main()
