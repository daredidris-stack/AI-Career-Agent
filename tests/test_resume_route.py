import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import HTTPException, UploadFile

from backend.routes.resume import analyze_resume_file
from backend.services.resume_service import (
    ProfileRequiredError,
    ResumeAnalysisError,
)


class ResumeRouteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=17)
        self.file = UploadFile(filename="resume.pdf", file=AsyncMock())
        self.service = AsyncMock()

    async def test_authenticated_user_is_passed_to_service(self):
        self.service.analyze_upload.return_value = {"resume_score": 82}

        result = await analyze_resume_file(
            self.file,
            self.user,
            self.service,
        )

        self.assertEqual(result["resume_score"], 82)
        self.service.analyze_upload.assert_awaited_once_with(self.file, 17)

    async def test_missing_profile_returns_404(self):
        self.service.analyze_upload.side_effect = ProfileRequiredError(
            "Create your profile."
        )

        with self.assertRaises(HTTPException) as context:
            await analyze_resume_file(self.file, self.user, self.service)

        self.assertEqual(context.exception.status_code, 404)

    async def test_invalid_upload_returns_400(self):
        self.service.analyze_upload.side_effect = ValueError("Unsupported")

        with self.assertRaises(HTTPException) as context:
            await analyze_resume_file(self.file, self.user, self.service)

        self.assertEqual(context.exception.status_code, 400)

    async def test_analysis_failure_returns_502(self):
        self.service.analyze_upload.side_effect = ResumeAnalysisError(
            "Invalid AI result"
        )

        with self.assertRaises(HTTPException) as context:
            await analyze_resume_file(self.file, self.user, self.service)

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
