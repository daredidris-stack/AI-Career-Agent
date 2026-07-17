import unittest
from types import SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import HTTPException

from backend.routes.resume_tailor import tailor_resume_upload
from backend.services.resume_tailor_service import (
    ProfileRequiredError,
    ResumeTailorError,
)


class ResumeTailorRouteTests(unittest.IsolatedAsyncioTestCase):
    async def test_authenticated_user_is_passed_to_service(self):
        service = SimpleNamespace(
            tailor_for_user=AsyncMock(
                return_value={
                    "summary": "",
                    "skills": [],
                    "experience": [],
                }
            )
        )
        file = object()

        result = await tailor_resume_upload(
            file=file,
            job_description="Cloud role",
            current_user=SimpleNamespace(id=12),
            service=service,
        )

        self.assertEqual(result["skills"], [])
        service.tailor_for_user.assert_awaited_once_with(
            user_id=12,
            file=file,
            job_description="Cloud role",
        )

    async def test_missing_profile_returns_404(self):
        service = SimpleNamespace(
            tailor_for_user=AsyncMock(
                side_effect=ProfileRequiredError(
                    "Create your profile."
                )
            )
        )

        with self.assertRaises(HTTPException) as context:
            await tailor_resume_upload(
                file=object(),
                job_description="Cloud role",
                current_user=SimpleNamespace(id=12),
                service=service,
            )

        self.assertEqual(context.exception.status_code, 404)

    async def test_invalid_input_returns_400(self):
        service = SimpleNamespace(
            tailor_for_user=AsyncMock(
                side_effect=ValueError("Unsupported file")
            )
        )

        with self.assertRaises(HTTPException) as context:
            await tailor_resume_upload(
                file=object(),
                job_description="Cloud role",
                current_user=SimpleNamespace(id=12),
                service=service,
            )

        self.assertEqual(context.exception.status_code, 400)

    async def test_ai_failure_returns_502(self):
        service = SimpleNamespace(
            tailor_for_user=AsyncMock(
                side_effect=ResumeTailorError(
                    "AI unavailable"
                )
            )
        )

        with self.assertRaises(HTTPException) as context:
            await tailor_resume_upload(
                file=object(),
                job_description="Cloud role",
                current_user=SimpleNamespace(id=12),
                service=service,
            )

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
