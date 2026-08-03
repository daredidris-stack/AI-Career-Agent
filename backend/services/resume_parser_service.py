import asyncio
import json
import os
import sys
from pathlib import Path

from backend.core.settings import (
    MAX_RESUME_UPLOAD_BYTES,
    RESUME_PARSER_MAX_CPU_SECONDS,
    RESUME_PARSER_MAX_MEMORY_MB,
    RESUME_PARSER_MAX_TEXT_CHARACTERS,
    RESUME_PARSER_TIMEOUT_SECONDS,
)


class ResumeParserError(ValueError):
    pass


class ResumeParserUnavailableError(Exception):
    pass


class ResumeParserService:
    WORKER_MODULE = "backend.jobs.parse_resume_document"
    PROJECT_ROOT = Path(__file__).resolve().parents[2]

    async def parse_file(self, file_path: Path, suffix: str) -> str:
        command = (
            sys.executable,
            "-m",
            self.WORKER_MODULE,
            str(file_path),
            suffix,
            str(MAX_RESUME_UPLOAD_BYTES),
            str(RESUME_PARSER_MAX_TEXT_CHARACTERS),
            str(RESUME_PARSER_MAX_MEMORY_MB),
            str(RESUME_PARSER_MAX_CPU_SECONDS),
        )
        try:
            process = await asyncio.create_subprocess_exec(
                *command,
                cwd=str(self.PROJECT_ROOT),
                env=self._worker_environment(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
            )
        except (OSError, RuntimeError) as error:
            raise ResumeParserUnavailableError(
                "Resume document processing is temporarily unavailable."
            ) from error

        try:
            stdout, _stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=RESUME_PARSER_TIMEOUT_SECONDS,
            )
        except asyncio.CancelledError:
            await self._stop_process(process)
            raise
        except TimeoutError as error:
            await self._stop_process(process)
            raise ResumeParserUnavailableError(
                "Resume document processing is temporarily unavailable."
            ) from error

        if process.returncode == 2:
            raise ResumeParserError(
                "The uploaded resume could not be read."
            )
        if process.returncode != 0:
            raise ResumeParserUnavailableError(
                "Resume document processing is temporarily unavailable."
            )

        maximum_response_bytes = (
            RESUME_PARSER_MAX_TEXT_CHARACTERS * 4 + 1024
        )
        if not stdout or len(stdout) > maximum_response_bytes:
            raise ResumeParserUnavailableError(
                "Resume document processing is temporarily unavailable."
            )

        try:
            payload = json.loads(stdout.decode("utf-8"))
            text = payload["text"]
        except (KeyError, TypeError, UnicodeDecodeError, json.JSONDecodeError) as error:
            raise ResumeParserUnavailableError(
                "Resume document processing is temporarily unavailable."
            ) from error

        if (
            payload.get("status") != "ok"
            or not isinstance(text, str)
            or not text.strip()
            or len(text) > RESUME_PARSER_MAX_TEXT_CHARACTERS
        ):
            raise ResumeParserError(
                "The uploaded resume does not contain readable text."
            )
        return text

    @staticmethod
    def _worker_environment() -> dict[str, str]:
        environment = {
            "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONUNBUFFERED": "1",
        }
        for name in ("LANG", "LC_ALL", "SYSTEMROOT"):
            value = os.environ.get(name)
            if value:
                environment[name] = value
        return environment

    @staticmethod
    async def _stop_process(process) -> None:
        if process.returncode is not None:
            return
        try:
            process.terminate()
        except ProcessLookupError:
            await process.wait()
            return
        try:
            await asyncio.wait_for(process.wait(), timeout=1)
        except TimeoutError:
            process.kill()
            await process.wait()
