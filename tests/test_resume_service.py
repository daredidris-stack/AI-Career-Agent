import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from fastapi import UploadFile

from backend.services.resume_service import ResumeService
from backend.services.resume_service import SUPPORTED_RESUME_TYPES


class ResumeServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_rejects_unsupported_file_types(self):
        service = ResumeService()
        file = UploadFile(
            filename="resume.txt",
            file=AsyncMock(),
        )
        file.close = AsyncMock()

        with self.assertRaisesRegex(
            ValueError,
            "Only PDF and DOCX",
        ):
            await service.analyze_upload(file, object())

        file.close.assert_awaited_once()

    @patch(
        "backend.services.resume_service.analyze_resume"
    )
    async def test_analyzes_upload_with_database_profile(
        self,
        mock_analyze_resume,
    ):
        mock_read_pdf = Mock(
            return_value="Resume text"
        )
        mock_analyze_resume.return_value = {
            "resume_score": 80,
            "ats_score": 75,
            "strengths": [],
            "improvements": [],
        }
        profile = SimpleNamespace(
            current_role="Technician",
            target_role="Cloud Engineer",
        )
        file = UploadFile(
            filename="resume.pdf",
            file=AsyncMock(),
        )
        file.read = AsyncMock(
            side_effect=[b"resume bytes", b""]
        )
        file.close = AsyncMock()

        with patch.dict(
            SUPPORTED_RESUME_TYPES,
            {".pdf": mock_read_pdf},
        ):
            result = await ResumeService().analyze_upload(
                file,
                profile,
            )

        self.assertEqual(result["resume_score"], 80)
        mock_analyze_resume.assert_called_once_with(
            "Resume text",
            profile,
        )
        file.close.assert_awaited_once()


if __name__ == "__main__":
    unittest.main()
