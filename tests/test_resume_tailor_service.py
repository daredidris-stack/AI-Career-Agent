import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from backend.services.resume_tailor_service import (
    ProfileRequiredError,
    ResumeTailorError,
    ResumeTailorService,
)


class ResumeTailorServiceTests(unittest.IsolatedAsyncioTestCase):
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
        self.resume_service = Mock()
        self.resume_service.extract_text = AsyncMock(
            return_value="Resume text"
        )

    @patch("backend.services.resume_tailor_service.chat")
    async def test_tailors_resume_with_database_profile(
        self,
        mock_chat,
    ):
        mock_chat.return_value.message.content = """
        {
            "summary": "Cloud professional",
            "skills": ["AWS"],
            "experience": ["Supported infrastructure"]
        }
        """
        service = ResumeTailorService(
            self.repository,
            self.resume_service,
        )

        result = await service.tailor_for_user(
            8,
            object(),
            "Cloud Engineer role",
        )

        self.repository.get_by_user_id.assert_called_once_with(8)
        self.assertEqual(result["skills"], ["AWS"])
        prompt = mock_chat.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Target role: Cloud Engineer", prompt)
        self.assertIn("Resume text", prompt)

    async def test_missing_profile_stops_processing(self):
        self.repository.get_by_user_id.return_value = None
        service = ResumeTailorService(
            self.repository,
            self.resume_service,
        )

        with self.assertRaises(ProfileRequiredError):
            await service.tailor_for_user(
                8,
                object(),
                "Cloud role",
            )

        self.resume_service.extract_text.assert_not_awaited()

    async def test_empty_job_description_is_rejected(self):
        service = ResumeTailorService(
            self.repository,
            self.resume_service,
        )

        with self.assertRaises(ValueError):
            await service.tailor_for_user(
                8,
                object(),
                "   ",
            )

    @patch("backend.services.resume_tailor_service.chat")
    async def test_uses_latest_saved_resume_when_file_is_omitted(
        self,
        mock_chat,
    ):
        mock_chat.return_value.message.content = """
        {"summary": "Cloud professional", "skills": ["AWS"],
         "experience": ["Supported infrastructure"]}
        """
        documents = Mock()
        documents.list_for_user.return_value = [SimpleNamespace(
            content="Latest saved resume",
            source_filename="saved.pdf",
            title="Saved resume",
        )]
        documents.create_for_user.return_value = SimpleNamespace(id=15)
        service = ResumeTailorService(
            self.repository,
            self.resume_service,
            documents,
        )

        await service.tailor_for_user(8, None, "Cloud role")

        documents.list_for_user.assert_called_once_with(8, "resume")
        prompt = mock_chat.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Latest saved resume", prompt)
        self.resume_service.extract_text.assert_not_awaited()

    @patch("backend.services.resume_tailor_service.chat")
    async def test_invalid_ai_response_returns_service_error(
        self,
        mock_chat,
    ):
        mock_chat.return_value.message.content = "not json"
        service = ResumeTailorService(
            self.repository,
            self.resume_service,
        )

        with self.assertRaises(ResumeTailorError):
            await service.tailor_for_user(
                8,
                object(),
                "Cloud role",
            )


if __name__ == "__main__":
    unittest.main()
