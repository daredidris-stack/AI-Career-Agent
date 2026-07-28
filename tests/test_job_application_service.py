import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.job_application_service import (
    ApplicationNotFoundError,
    JobApplicationService,
)


class JobApplicationServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.document_repository = Mock()
        self.service = JobApplicationService(
            self.repository,
            self.document_repository,
        )

    def test_create_assigns_owner_and_applied_date(self):
        self.service.create_for_user(
            7,
            {"company": " Example ", "role": " SRE ", "status": "applied"},
        )

        values = self.repository.create.call_args.kwargs
        self.assertEqual(values["user_id"], 7)
        self.assertEqual(values["company"], "Example")
        self.assertEqual(values["role"], "SRE")
        self.assertIsNotNone(values["applied_at"])

    def test_invalid_status_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            self.service.create_for_user(
                7,
                {"company": "Example", "role": "SRE", "status": "hired"},
            )

        self.repository.create.assert_not_called()

    def test_prepare_validates_documents_and_records_review(self):
        documents = {
            11: SimpleNamespace(id=11, kind="tailored_resume"),
            12: SimpleNamespace(id=12, kind="cover_letter"),
        }
        self.document_repository.get_for_user.side_effect = (
            lambda document_id, _user_id: documents.get(document_id)
        )
        self.repository.get_by_job_url.return_value = None

        self.service.prepare_for_user(
            7,
            {
                "company": " Example ",
                "role": " SRE ",
                "job_url": "https://jobs.example.com/sre",
                "location": " Remote ",
                "source": "Greenhouse",
                "source_job_id": "job-1",
                "resume_document_id": 11,
                "cover_letter_document_id": 12,
                "review_confirmed": True,
                "manual_submission_confirmed": True,
            },
        )

        values = self.repository.create.call_args.kwargs
        self.assertEqual(values["user_id"], 7)
        self.assertEqual(values["status"], "preparing")
        self.assertEqual(values["company"], "Example")
        self.assertEqual(values["resume_document_id"], 11)
        self.assertEqual(values["cover_letter_document_id"], 12)
        self.assertIsNotNone(values["package_reviewed_at"])

    def test_prepare_requires_explicit_confirmation(self):
        with self.assertRaisesRegex(ValueError, "Review"):
            self.service.prepare_for_user(
                7,
                {
                    "company": "Example",
                    "role": "SRE",
                    "job_url": "https://jobs.example.com/sre",
                    "resume_document_id": 11,
                    "review_confirmed": False,
                    "manual_submission_confirmed": True,
                },
            )

        self.repository.create.assert_not_called()

    def test_prepare_rejects_unsafe_application_url(self):
        with self.assertRaisesRegex(ValueError, "secure official"):
            self.service.prepare_for_user(
                7,
                {
                    "company": "Example",
                    "role": "SRE",
                    "job_url": "javascript:alert(1)",
                    "resume_document_id": 11,
                    "review_confirmed": True,
                    "manual_submission_confirmed": True,
                },
            )

        self.repository.create.assert_not_called()

    def test_prepare_rejects_document_owned_by_another_user(self):
        self.document_repository.get_for_user.return_value = None

        with self.assertRaisesRegex(ValueError, "resume is not available"):
            self.service.prepare_for_user(
                7,
                {
                    "company": "Example",
                    "role": "SRE",
                    "job_url": "https://jobs.example.com/sre",
                    "resume_document_id": 11,
                    "review_confirmed": True,
                    "manual_submission_confirmed": True,
                },
            )

        self.document_repository.get_for_user.assert_called_once_with(11, 7)
        self.repository.create.assert_not_called()

    def test_prepare_reuses_existing_application_without_downgrading(self):
        self.document_repository.get_for_user.return_value = SimpleNamespace(
            id=11,
            kind="resume",
        )
        existing = SimpleNamespace(
            company="Example",
            role="SRE",
            job_url="https://jobs.example.com/sre",
            status="applied",
            package_reviewed_at=None,
        )
        self.repository.get_by_job_url.return_value = existing

        self.service.prepare_for_user(
            7,
            {
                "company": "Example",
                "role": "SRE",
                "job_url": "https://jobs.example.com/sre",
                "resume_document_id": 11,
                "review_confirmed": True,
                "manual_submission_confirmed": True,
            },
        )

        self.assertEqual(existing.status, "applied")
        self.assertEqual(existing.resume_document_id, 11)
        self.assertIsNotNone(existing.package_reviewed_at)
        self.repository.create.assert_not_called()
        self.repository.save.assert_called_once_with(existing)

    def test_update_cannot_access_another_users_application(self):
        self.repository.get_for_user.return_value = None

        with self.assertRaises(ApplicationNotFoundError):
            self.service.update_for_user(
                7,
                99,
                {"company": "Example", "role": "SRE", "status": "saved"},
            )

        self.repository.get_for_user.assert_called_once_with(99, 7)
        self.repository.save.assert_not_called()

    def test_move_to_applied_records_first_application_date(self):
        application = SimpleNamespace(
            company="Example",
            role="SRE",
            status="saved",
            applied_at=None,
        )
        self.repository.get_for_user.return_value = application

        self.service.update_for_user(
            7,
            3,
            {"company": "Example", "role": "SRE", "status": "applied"},
        )

        self.assertEqual(application.status, "applied")
        self.assertIsNotNone(application.applied_at)
        self.repository.save.assert_called_once_with(application)

    def test_delete_uses_owner_scoped_lookup(self):
        application = SimpleNamespace(id=3)
        self.repository.get_for_user.return_value = application

        self.service.delete_for_user(7, 3)

        self.repository.get_for_user.assert_called_once_with(3, 7)
        self.repository.delete.assert_called_once_with(application)


if __name__ == "__main__":
    unittest.main()
