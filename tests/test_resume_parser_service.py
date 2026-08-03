import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

from reportlab.pdfgen.canvas import Canvas

from backend.services.resume_parser_service import (
    ResumeParserError,
    ResumeParserService,
    ResumeParserUnavailableError,
)


class FakeProcess:
    def __init__(self, returncode=0, stdout=b""):
        self.returncode = returncode
        self.communicate = AsyncMock(return_value=(stdout, None))
        self.wait = AsyncMock(return_value=returncode)
        self.terminate = Mock()
        self.kill = Mock()


class ResumeParserServiceTests(unittest.IsolatedAsyncioTestCase):
    @patch(
        "backend.services.resume_parser_service.asyncio.create_subprocess_exec",
        new_callable=AsyncMock,
    )
    async def test_returns_worker_text_without_inheriting_secrets(
        self,
        create_process,
    ):
        process = FakeProcess(
            stdout=json.dumps({
                "status": "ok",
                "text": "Resume text",
            }).encode()
        )
        create_process.return_value = process
        service = ResumeParserService()

        with patch.dict(
            os.environ,
            {
                "DATABASE_URL": "secret-database",
                "JWT_SECRET_KEY": "secret-jwt",
                "LANG": "en_US.UTF-8",
            },
            clear=True,
        ):
            result = await service.parse_file(
                Path("/private/tmp/resume.pdf"),
                ".pdf",
            )

        self.assertEqual(result, "Resume text")
        environment = create_process.await_args.kwargs["env"]
        self.assertEqual(environment["LANG"], "en_US.UTF-8")
        self.assertNotIn("DATABASE_URL", environment)
        self.assertNotIn("JWT_SECRET_KEY", environment)
        self.assertIn(
            "backend.jobs.parse_resume_document",
            create_process.await_args.args,
        )

    @patch(
        "backend.services.resume_parser_service.asyncio.create_subprocess_exec",
        new_callable=AsyncMock,
    )
    async def test_worker_rejection_is_a_generic_upload_error(
        self,
        create_process,
    ):
        create_process.return_value = FakeProcess(
            returncode=2,
            stdout=b'{"status":"invalid"}',
        )

        with self.assertRaisesRegex(
            ResumeParserError,
            "could not be read",
        ):
            await ResumeParserService().parse_file(
                Path("/private/tmp/resume.pdf"),
                ".pdf",
            )

    @patch(
        "backend.services.resume_parser_service.asyncio.create_subprocess_exec",
        new_callable=AsyncMock,
    )
    async def test_worker_failure_is_unavailable_without_internal_details(
        self,
        create_process,
    ):
        create_process.return_value = FakeProcess(
            returncode=3,
            stdout=b'{"status":"unavailable","detail":"internal"}',
        )

        with self.assertRaisesRegex(
            ResumeParserUnavailableError,
            "temporarily unavailable",
        ) as context:
            await ResumeParserService().parse_file(
                Path("/private/tmp/resume.pdf"),
                ".pdf",
            )

        self.assertNotIn("internal", str(context.exception))

    @patch(
        "backend.services.resume_parser_service.RESUME_PARSER_TIMEOUT_SECONDS",
        0.01,
    )
    @patch(
        "backend.services.resume_parser_service.asyncio.create_subprocess_exec",
        new_callable=AsyncMock,
    )
    async def test_timeout_terminates_worker(
        self,
        create_process,
    ):
        process = FakeProcess()
        process.returncode = None
        process.communicate.side_effect = TimeoutError()

        def mark_terminated():
            process.returncode = -15

        process.terminate.side_effect = mark_terminated
        create_process.return_value = process

        with self.assertRaises(ResumeParserUnavailableError):
            await ResumeParserService().parse_file(
                Path("/private/tmp/resume.pdf"),
                ".pdf",
            )

        process.terminate.assert_called_once()
        process.wait.assert_awaited_once()

    @patch(
        "backend.services.resume_parser_service.asyncio.create_subprocess_exec",
        new_callable=AsyncMock,
    )
    async def test_request_cancellation_terminates_worker(
        self,
        create_process,
    ):
        process = FakeProcess()
        process.returncode = None
        communication_started = asyncio.Event()

        async def wait_forever():
            communication_started.set()
            await asyncio.Event().wait()

        process.communicate.side_effect = wait_forever

        def mark_terminated():
            process.returncode = -15

        process.terminate.side_effect = mark_terminated
        create_process.return_value = process

        task = asyncio.create_task(
            ResumeParserService().parse_file(
                Path("/private/tmp/resume.pdf"),
                ".pdf",
            )
        )
        await communication_started.wait()
        task.cancel()

        with self.assertRaises(asyncio.CancelledError):
            await task

        process.terminate.assert_called_once()
        process.wait.assert_awaited_once()

    @patch(
        "backend.services.resume_parser_service.asyncio.create_subprocess_exec",
        new_callable=AsyncMock,
    )
    async def test_invalid_success_payload_fails_closed(
        self,
        create_process,
    ):
        create_process.return_value = FakeProcess(stdout=b"not-json")

        with self.assertRaises(ResumeParserUnavailableError):
            await ResumeParserService().parse_file(
                Path("/private/tmp/resume.pdf"),
                ".pdf",
            )

    async def test_real_worker_parses_docx_in_a_subprocess(self):
        template = (
            ResumeParserService.PROJECT_ROOT
            / "backend"
            / "templates"
            / "ats_tailored_resume_template.docx"
        )

        text = await ResumeParserService().parse_file(template, ".docx")

        self.assertIn("PROFESSIONAL SUMMARY", text)
        self.assertIn("{{FULL_NAME}}", text)

    async def test_real_worker_parses_pdf_in_a_subprocess(self):
        with tempfile.NamedTemporaryFile(
            suffix=".pdf",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
        try:
            document = Canvas(str(temporary_path))
            document.drawString(72, 720, "Cloud Engineer Resume")
            document.save()

            text = await ResumeParserService().parse_file(
                temporary_path,
                ".pdf",
            )
        finally:
            temporary_path.unlink(missing_ok=True)

        self.assertIn("Cloud Engineer Resume", text)

    @patch(
        "backend.services.resume_parser_service."
        "RESUME_PARSER_MAX_TEXT_CHARACTERS",
        20,
    )
    async def test_real_worker_enforces_extracted_text_limit(self):
        template = (
            ResumeParserService.PROJECT_ROOT
            / "backend"
            / "templates"
            / "ats_tailored_resume_template.docx"
        )

        with self.assertRaises(ResumeParserError):
            await ResumeParserService().parse_file(template, ".docx")


if __name__ == "__main__":
    unittest.main()
