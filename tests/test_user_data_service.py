import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import Mock

from backend.models.profile import Profile
from backend.services.user_data_service import UserDataService


class UserDataServiceTests(unittest.TestCase):
    def test_export_excludes_password_and_serializes_owned_data(self):
        repository = Mock()
        repository.snapshot.return_value = {
            "profile": Profile(id=2, user_id=7, city="Queretaro"),
            "resume_analyses": [],
            "career_documents": [],
            "document_revisions": [],
            "job_applications": [],
            "ai_usage_events": [],
        }
        user = SimpleNamespace(
            id=7,
            email="user@example.com",
            first_name="Ada",
            last_name="Lovelace",
            password_hash="must-not-export",
            created_at=datetime(2026, 1, 1),
            is_email_verified=True,
        )

        result = UserDataService(repository).export_for_user(user)

        repository.snapshot.assert_called_once_with(7)
        self.assertNotIn("password_hash", result["account"])
        self.assertNotIn("user_id", result["profile"])
        self.assertEqual(result["profile"]["city"], "Queretaro")


if __name__ == "__main__":
    unittest.main()
