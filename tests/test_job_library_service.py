import json
import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.job_library_service import JobLibraryService


class JobLibraryServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = JobLibraryService(self.repository)
        self.job = {
            "title": "Platform Engineer",
            "company": "Example",
            "source": "Greenhouse",
            "source_job_id": "job-1",
            "location": "Remote",
            "listing_url": "https://jobs.example.com/job-1",
        }

    def test_save_job_reuses_owner_job_key(self):
        self.repository.get_saved_job_by_key.return_value = None
        created = SimpleNamespace(
            id=4,
            job_key=self.service.job_key(self.job),
            job_data_json=json.dumps(self.job),
            created_at=None,
            updated_at=None,
        )
        self.repository.create_saved_job.return_value = created

        result = self.service.save_job(9, self.job)

        self.assertEqual(result["id"], 4)
        self.repository.get_saved_job_by_key.assert_called_once_with(
            9,
            created.job_key,
        )
        self.repository.create_saved_job.assert_called_once()

    def test_save_job_rejects_unsafe_or_missing_provider_url(self):
        with self.assertRaisesRegex(
            ValueError,
            "secure provider job URL",
        ):
            self.service.save_job(
                9,
                {
                    **self.job,
                    "listing_url": "javascript:alert(1)",
                },
            )

        with self.assertRaisesRegex(
            ValueError,
            "secure provider job URL",
        ):
            self.service.save_job(
                9,
                {
                    **self.job,
                    "source_job_id": None,
                    "listing_url": None,
                },
            )

    def test_search_alerts_use_first_run_as_baseline(self):
        saved_search = SimpleNamespace(
            id=2,
            name="SRE",
            filters_json='{"keyword": "SRE"}',
            seen_job_keys_json="[]",
            new_match_count=0,
            last_result_count=0,
            last_run_at=None,
            created_at=None,
            updated_at=None,
        )
        self.repository.save_search.side_effect = lambda item: item

        first = self.service.record_search_results(
            saved_search,
            [self.job],
        )
        second = self.service.record_search_results(
            saved_search,
            [
                self.job,
                {
                    **self.job,
                    "source_job_id": "job-2",
                    "listing_url": "https://jobs.example.com/job-2",
                },
            ],
        )

        self.assertEqual(first["new_match_count"], 0)
        self.assertEqual(second["new_match_count"], 1)
        self.assertEqual(second["last_result_count"], 2)


if __name__ == "__main__":
    unittest.main()
