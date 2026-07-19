import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.routes.job_search import search_jobs
from backend.services.job_search_service import (
    JobSearchInputError,
    JobSearchError,
)


class JobSearchRouteTests(unittest.TestCase):
    def test_authenticated_user_id_is_passed_to_service(self):
        service = Mock()
        service.search_for_user.return_value = {
            "count": 0,
            "filters": {},
            "jobs": [],
        }

        result = search_jobs(
            keyword="cloud",
            current_user=SimpleNamespace(id=7),
            service=service,
        )

        self.assertEqual(result["count"], 0)
        service.search_for_user.assert_called_once_with(
            user_id=7,
            keyword="cloud",
            country=None,
            city=None,
            industry=None,
            work_mode=None,
            employment_type=None,
            posted_within_days=0,
            min_salary=0,
            min_score=0,
            page=1,
            per_page=20,
        )

    def test_missing_search_role_returns_400(self):
        service = Mock()
        service.search_for_user.side_effect = (
            JobSearchInputError("Enter a target role.")
        )

        with self.assertRaises(HTTPException) as context:
            search_jobs(
                keyword="cloud",
                current_user=SimpleNamespace(id=7),
                service=service,
            )

        self.assertEqual(context.exception.status_code, 400)

    def test_service_failure_returns_502(self):
        service = Mock()
        service.search_for_user.side_effect = JobSearchError(
            "Job search is temporarily unavailable."
        )

        with self.assertRaises(HTTPException) as context:
            search_jobs(
                keyword="cloud",
                current_user=SimpleNamespace(id=7),
                service=service,
            )

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
