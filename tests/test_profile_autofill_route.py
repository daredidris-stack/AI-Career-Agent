import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from fastapi import HTTPException, UploadFile

from backend.routes.profile import autofill_profile
from backend.services.profile_autofill_service import ProfileAutofillError
from backend.services.malware_scan_service import (
    MalwareScannerUnavailableError,
)
from backend.services.resume_parser_service import (
    ResumeParserUnavailableError,
)


class ProfileAutofillRouteTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=17)
        self.file = UploadFile(filename="resume.pdf", file=AsyncMock())
        self.service = AsyncMock()
        self.usage = Mock()

    async def test_authenticated_user_can_autofill_without_existing_profile(self):
        self.service.autofill_upload.return_value = {
            "current_role": "Technician"
        }

        result = await autofill_profile(
            self.file,
            self.user,
            self.service,
            self.usage,
        )

        self.assertEqual(result["current_role"], "Technician")
        self.usage.reserve.assert_called_once_with(17, "profile_autofill")
        self.service.autofill_upload.assert_awaited_once_with(self.file)

    async def test_invalid_resume_returns_400(self):
        self.service.autofill_upload.side_effect = ValueError("Unsupported")

        with self.assertRaises(HTTPException) as context:
            await autofill_profile(
                self.file,
                self.user,
                self.service,
                self.usage,
            )

        self.assertEqual(context.exception.status_code, 400)

    async def test_ai_failure_returns_502(self):
        self.service.autofill_upload.side_effect = ProfileAutofillError(
            "AI unavailable"
        )

        with self.assertRaises(HTTPException) as context:
            await autofill_profile(
                self.file,
                self.user,
                self.service,
                self.usage,
            )

        self.assertEqual(context.exception.status_code, 502)

    async def test_unavailable_security_scanner_returns_503(self):
        self.service.autofill_upload.side_effect = (
            MalwareScannerUnavailableError("Scanner unavailable")
        )

        with self.assertRaises(HTTPException) as context:
            await autofill_profile(
                self.file,
                self.user,
                self.service,
                self.usage,
            )

        self.assertEqual(context.exception.status_code, 503)

    async def test_unavailable_document_parser_returns_503(self):
        self.service.autofill_upload.side_effect = (
            ResumeParserUnavailableError("Parser unavailable")
        )

        with self.assertRaises(HTTPException) as context:
            await autofill_profile(
                self.file,
                self.user,
                self.service,
                self.usage,
            )

        self.assertEqual(context.exception.status_code, 503)


if __name__ == "__main__":
    unittest.main()
