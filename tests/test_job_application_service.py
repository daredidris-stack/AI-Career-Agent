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
        self.service = JobApplicationService(self.repository)

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
