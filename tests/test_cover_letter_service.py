import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.services.cover_letter_service import (
    CoverLetterError,
    CoverLetterService,
    ProfileRequiredError,
)


class CoverLetterServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            current_role="Technician",
            target_role="Cloud Engineer",
            years_experience=4,
            technical_skills="AWS, Linux, Python",
            professional_summary="Infrastructure operations",
        )
        self.repository = Mock()
        self.repository.get_by_user_id.return_value = self.profile
        self.service = CoverLetterService(self.repository)

    @patch("backend.services.cover_letter_service.chat")
    def test_generates_cover_letter_with_profile_context(
        self,
        mock_chat,
    ):
        mock_chat.return_value.message.content = (
            "Dear Hiring Manager,\n\nLetter body"
        )

        result = self.service.generate_for_user(
            5,
            "Supported AWS infrastructure.",
            "Cloud Engineer role",
        )

        self.repository.get_by_user_id.assert_called_once_with(5)
        self.assertEqual(
            result,
            {
                "cover_letter": (
                    "Dear Hiring Manager,\n\nLetter body"
                )
            },
        )
        prompt = mock_chat.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Target role: Cloud Engineer", prompt)
        self.assertIn("Supported AWS infrastructure.", prompt)

    def test_empty_resume_is_rejected_before_profile_lookup(self):
        with self.assertRaisesRegex(
            ValueError,
            "Resume cannot be empty",
        ):
            self.service.generate_for_user(
                5,
                "   ",
                "Cloud role",
            )

        self.repository.get_by_user_id.assert_not_called()

    def test_empty_job_description_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "Job description cannot be empty",
        ):
            self.service.generate_for_user(
                5,
                "Resume",
                "   ",
            )

    def test_missing_profile_stops_generation(self):
        self.repository.get_by_user_id.return_value = None

        with self.assertRaises(ProfileRequiredError):
            self.service.generate_for_user(
                5,
                "Resume",
                "Cloud role",
            )

    @patch("backend.services.cover_letter_service.chat")
    def test_ai_failure_returns_service_error(
        self,
        mock_chat,
    ):
        mock_chat.side_effect = RuntimeError("Ollama unavailable")

        with self.assertRaises(CoverLetterError):
            self.service.generate_for_user(
                5,
                "Resume",
                "Cloud role",
            )

    @patch("backend.services.cover_letter_service.chat")
    def test_empty_ai_response_returns_service_error(
        self,
        mock_chat,
    ):
        mock_chat.return_value.message.content = "   "

        with self.assertRaises(CoverLetterError):
            self.service.generate_for_user(
                5,
                "Resume",
                "Cloud role",
            )

    @patch("backend.services.cover_letter_service.chat")
    def test_generated_letter_is_saved_to_document_library(self, mock_chat):
        mock_chat.return_value.message.content = "Letter body"
        documents = Mock()
        documents.create_for_user.return_value = SimpleNamespace(id=12)
        service = CoverLetterService(self.repository, documents)

        result = service.generate_for_user(5, "Resume", "Cloud role")

        self.assertEqual(result["document_id"], 12)
        documents.create_for_user.assert_called_once_with(
            5,
            "cover_letter",
            "Cover Letter",
            "Letter body",
            job_description="Cloud role",
        )


if __name__ == "__main__":
    unittest.main()
