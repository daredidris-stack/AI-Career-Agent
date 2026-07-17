from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import Any

from fastapi import UploadFile

from docx_reader import read_docx_resume
from resume_analyzer import analyze_resume
from resume_reader import read_pdf_resume
from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)
from backend.services.candidate_skills import normalize_explicit_skills
from backend.services.career_document_service import CareerDocumentService
from backend.core.settings import MAX_RESUME_UPLOAD_BYTES


SUPPORTED_RESUME_TYPES = {
    ".docx": read_docx_resume,
    ".pdf": read_pdf_resume,
}
FILE_SIGNATURES = {
    ".pdf": (b"%PDF",),
    ".docx": (b"PK\x03\x04", b"PK\x05\x06", b"PK\x07\x08"),
}


class ResumeService:
    def __init__(
        self,
        profile_repository: ProfileRepository,
        analysis_repository: ResumeAnalysisRepository,
        document_service: CareerDocumentService | None = None,
    ):
        self.profile_repository = profile_repository
        self.analysis_repository = analysis_repository
        self.document_service = document_service

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
        total_bytes = 0
        first_chunk = True

        try:
            with NamedTemporaryFile(
                suffix=suffix,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)

                while chunk := await file.read(1024 * 1024):
                    total_bytes += len(chunk)
                    if total_bytes > MAX_RESUME_UPLOAD_BYTES:
                        raise ValueError(
                            "Resume files must be 5 MB or smaller."
                        )
                    if first_chunk:
                        first_chunk = False
                        if not chunk.startswith(FILE_SIGNATURES[suffix]):
                            raise ValueError(
                                "The uploaded file content does not match its extension."
                            )
                    temporary_file.write(chunk)

            if total_bytes == 0:
                raise ValueError("The uploaded resume is empty.")

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
        user_id: int,
    ) -> dict:
        profile = self.profile_repository.get_by_user_id(user_id)

        if not profile:
            await file.close()
            raise ProfileRequiredError(
                "Create your profile before analyzing a resume."
            )

        filename = file.filename or "resume"
        resume_text = await self.extract_text(file)
        try:
            raw_result = analyze_resume(resume_text, profile)
        except Exception as error:
            raise ResumeAnalysisError(
                "Resume analysis is temporarily unavailable."
            ) from error

        result = self._normalize_result(raw_result)

        try:
            self.analysis_repository.create(user_id, filename, result)
            document = None
            if self.document_service:
                document = self.document_service.create_for_user(
                    user_id,
                    "resume",
                    filename,
                    resume_text,
                    source_filename=filename,
                    metadata={
                        "resume_score": result["resume_score"],
                        "ats_score": result["ats_score"],
                        "skills": result["skills"],
                    },
                )
        except Exception as error:
            raise ResumeAnalysisError(
                "Resume analysis could not be saved."
            ) from error

        return {
            **result,
            **({"document_id": document.id} if document else {}),
        }

    @staticmethod
    def _normalize_result(result: Any) -> dict[str, Any]:
        if not isinstance(result, dict):
            raise ResumeAnalysisError("Resume analysis returned invalid data.")

        try:
            resume_score = max(0, min(100, int(result["resume_score"])))
            ats_score = max(0, min(100, int(result["ats_score"])))
        except (KeyError, TypeError, ValueError) as error:
            raise ResumeAnalysisError(
                "Resume analysis returned invalid scores."
            ) from error

        return {
            "resume_score": resume_score,
            "ats_score": ats_score,
            "strengths": list(result.get("strengths") or []),
            "improvements": list(result.get("improvements") or []),
            "skills": ResumeService._normalize_skills(
                result.get("skills")
            ),
        }

    @staticmethod
    def _normalize_skills(skills: Any) -> list[str]:
        return normalize_explicit_skills(skills)


class ProfileRequiredError(Exception):
    pass


class ResumeAnalysisError(Exception):
    pass
