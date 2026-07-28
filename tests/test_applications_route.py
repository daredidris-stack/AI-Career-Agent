import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from fastapi import HTTPException

from backend.models.schemas import JobApplicationPrepare
from backend.routes.applications import prepare_application


class ApplicationsRouteTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=10)
        self.service = Mock()
        self.request = JobApplicationPrepare(
            company="Example",
            role="SRE",
            job_url="https://jobs.example.com/sre",
            location="Remote",
            source="Greenhouse",
            source_job_id="job-1",
            resume_document_id=11,
            cover_letter_document_id=12,
            review_confirmed=True,
            manual_submission_confirmed=True,
        )

    def test_prepare_passes_authenticated_owner_and_payload(self):
        prepared = SimpleNamespace(id=3, status="preparing")
        self.service.prepare_for_user.return_value = prepared

        result = prepare_application(
            self.request,
            self.user,
            self.service,
        )

        self.assertIs(result, prepared)
        self.service.prepare_for_user.assert_called_once_with(
            10,
            self.request.model_dump(),
        )

    def test_prepare_validation_error_returns_400(self):
        self.service.prepare_for_user.side_effect = ValueError(
            "The selected resume is not available."
        )

        with self.assertRaises(HTTPException) as context:
            prepare_application(
                self.request,
                self.user,
                self.service,
            )

        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(
            context.exception.detail,
            "The selected resume is not available.",
        )


if __name__ == "__main__":
    unittest.main()
