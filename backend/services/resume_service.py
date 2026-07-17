from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from fastapi import UploadFile

from docx_reader import read_docx_resume
from resume_analyzer import analyze_resume
from resume_reader import read_pdf_resume


SUPPORTED_RESUME_TYPES = {
    ".docx": read_docx_resume,
    ".pdf": read_pdf_resume,
}


class ResumeService:
    async def extract_text(
        self,
        file: UploadFile,
    ) -> str:
        suffix = Path(file.filename or "").suffix.lower()
        resume_reader = SUPPORTED_RESUME_TYPES.get(suffix)

        if not resume_reader:
            await file.close()
            raise ValueError(
                "Only PDF and DOCX files are supported."
            )

        temporary_path = None

        try:
            with NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                while chunk := await file.read(1024 * 1024):
                    temporary_file.write(chunk)

            return resume_reader(
                str(temporary_path)
            )
        finally:
            await file.close()

            if temporary_path:
                temporary_path.unlink(missing_ok=True)

    async def analyze_upload(
        self,
        file: UploadFile,
        profile: Any,
    ) -> dict:
        resume_text = await self.extract_text(file)

        return analyze_resume(
            resume_text,
            profile,
        )
