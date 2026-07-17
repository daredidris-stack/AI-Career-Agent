import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from fastapi import UploadFile

from backend.services.resume_service import ResumeService
from backend.services.resume_service import (
    ProfileRequiredError,
    ResumeAnalysisError,
    SUPPORTED_RESUME_TYPES,
)


class ResumeServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            current_role="Technician",
            target_role="Cloud Engineer",
        )
        self.profile_repository = Mock()
        self.profile_repository.get_by_user_id.return_value = self.profile
        self.analysis_repository = Mock()
        self.service = ResumeService(
            self.profile_repository,
            self.analysis_repository,
        )

    async def test_rejects_unsupported_file_types(self):
        file = UploadFile(
            filename="resume.txt",
            file=AsyncMock(),
        )
        file.close = AsyncMock()

        with self.assertRaisesRegex(
            ValueError,
            "Only PDF and DOCX",
        ):
            await self.service.analyze_upload(file, 3)

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
            "skills": ["AWS", "Linux", "aws"],
        }
        file = UploadFile(
            filename="resume.pdf",
            file=AsyncMock(),
        )
        file.read = AsyncMock(
            side_effect=[b"%PDF resume bytes", b""]
        )
        file.close = AsyncMock()

        with patch.dict(
            SUPPORTED_RESUME_TYPES,
            {".pdf": mock_read_pdf},
        ):
            result = await self.service.analyze_upload(
                file,
                3,
            )

        self.assertEqual(result["resume_score"], 80)
        self.assertEqual(result["skills"], ["AWS", "Linux"])
        mock_analyze_resume.assert_called_once_with(
            "Resume text",
            self.profile,
        )
        self.analysis_repository.create.assert_called_once_with(
            3,
            "resume.pdf",
            result,
        )
        file.close.assert_awaited_once()

    async def test_missing_profile_stops_analysis(self):
        self.profile_repository.get_by_user_id.return_value = None
        file = UploadFile(filename="resume.pdf", file=AsyncMock())
        file.close = AsyncMock()

        with self.assertRaises(ProfileRequiredError):
            await self.service.analyze_upload(file, 3)

        file.close.assert_awaited_once()
        self.analysis_repository.create.assert_not_called()

    async def test_rejects_file_with_spoofed_extension(self):
        file = UploadFile(filename="resume.pdf", file=AsyncMock())
        file.read = AsyncMock(side_effect=[b"not really a PDF", b""])
        file.close = AsyncMock()

        with self.assertRaisesRegex(ValueError, "does not match"):
            await self.service.extract_text(file)

        file.close.assert_awaited_once()

    @patch("backend.services.resume_service.MAX_RESUME_UPLOAD_BYTES", 8)
    async def test_rejects_oversized_file(self):
        file = UploadFile(filename="resume.pdf", file=AsyncMock())
        file.read = AsyncMock(side_effect=[b"%PDF too large", b""])
        file.close = AsyncMock()

        with self.assertRaisesRegex(ValueError, "5 MB or smaller"):
            await self.service.extract_text(file)

        file.close.assert_awaited_once()

    def test_normalizes_and_clamps_scores(self):
        result = self.service._normalize_result({
            "resume_score": 120,
            "ats_score": "-4",
            "strengths": ["Clear structure"],
            "skills": ["AWS", " aws ", "Python"],
        })

        self.assertEqual(result["resume_score"], 100)
        self.assertEqual(result["ats_score"], 0)
        self.assertEqual(result["improvements"], [])
        self.assertEqual(result["skills"], ["AWS", "Python"])

    def test_rejects_invalid_scores(self):
        with self.assertRaises(ResumeAnalysisError):
            self.service._normalize_result({"resume_score": "invalid"})

    @patch(
        "backend.services.resume_service.analyze_resume",
        side_effect=RuntimeError("AI unavailable"),
    )
    async def test_ai_failure_is_not_persisted(self, _mock_analyze_resume):
        file = UploadFile(filename="resume.pdf", file=AsyncMock())
        file.read = AsyncMock(side_effect=[b"%PDF resume bytes", b""])
        file.close = AsyncMock()

        with patch.dict(
            SUPPORTED_RESUME_TYPES,
            {".pdf": Mock(return_value="Resume text")},
        ):
            with self.assertRaises(ResumeAnalysisError):
                await self.service.analyze_upload(file, 3)

        self.analysis_repository.create.assert_not_called()

    @patch(
        "backend.services.resume_service.analyze_resume",
        return_value={"resume_score": 80, "ats_score": 75},
    )
    async def test_persistence_failure_is_reported(
        self,
        _mock_analyze_resume,
    ):
        self.analysis_repository.create.side_effect = RuntimeError(
            "Database unavailable"
        )
        file = UploadFile(filename="resume.pdf", file=AsyncMock())
        file.read = AsyncMock(side_effect=[b"%PDF resume bytes", b""])
        file.close = AsyncMock()

        with patch.dict(
            SUPPORTED_RESUME_TYPES,
            {".pdf": Mock(return_value="Resume text")},
        ):
            with self.assertRaises(ResumeAnalysisError):
                await self.service.analyze_upload(file, 3)


if __name__ == "__main__":
    unittest.main()
