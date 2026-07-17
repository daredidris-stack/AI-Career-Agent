import json
from typing import Any

from backend.repositories.career_document_repository import (
    CareerDocumentRepository,
)


DOCUMENT_KINDS = {
    "resume",
    "tailored_resume",
    "cover_letter",
    "job_match",
}


class DocumentNotFoundError(Exception):
    pass


class CareerDocumentService:
    def __init__(self, repository: CareerDocumentRepository):
        self.repository = repository

    def list_for_user(self, user_id: int, kind: str | None = None):
        if kind and kind not in DOCUMENT_KINDS:
            raise ValueError("Unsupported document type.")
        return self.repository.list_for_user(user_id, kind)

    def get_for_user(self, user_id: int, document_id: int):
        document = self.repository.get_for_user(document_id, user_id)
        if not document:
            raise DocumentNotFoundError()
        return document

    def create_for_user(
        self,
        user_id: int,
        kind: str,
        title: str,
        content: str,
        source_filename: str | None = None,
        job_description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        if kind not in DOCUMENT_KINDS:
            raise ValueError("Unsupported document type.")
        title = title.strip()
        content = content.strip()
        if not title or not content:
            raise ValueError("Document title and content are required.")
        return self.repository.create(
            user_id=user_id,
            kind=kind,
            title=title,
            content=content,
            source_filename=source_filename,
            job_description=job_description,
            metadata_json=json.dumps(metadata or {}),
        )

    def update_for_user(
        self,
        user_id: int,
        document_id: int,
        title: str,
        content: str,
    ):
        document = self.get_for_user(user_id, document_id)
        if not title.strip() or not content.strip():
            raise ValueError("Document title and content are required.")
        document.title = title.strip()
        document.content = content.strip()
        return self.repository.save(document)

    def delete_for_user(self, user_id: int, document_id: int) -> None:
        document = self.get_for_user(user_id, document_id)
        self.repository.delete(document)
