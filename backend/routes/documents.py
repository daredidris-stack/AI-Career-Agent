from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse
from io import BytesIO

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_career_document_service
from backend.models.schemas import (
    CareerDocumentCreate,
    CareerDocumentResponse,
    CareerDocumentUpdate,
)
from backend.models.user import User
from backend.services.career_document_service import (
    CareerDocumentService,
    DocumentNotFoundError,
)
from backend.services.document_export_service import export_document


router = APIRouter(prefix="/documents", tags=["Career Documents"])


@router.get("", response_model=list[CareerDocumentResponse])
def list_documents(
    kind: str | None = None,
    current_user: User = Depends(get_current_user),
    service: CareerDocumentService = Depends(get_career_document_service),
):
    try:
        return service.list_for_user(current_user.id, kind)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.get("/{document_id}", response_model=CareerDocumentResponse)
def get_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: CareerDocumentService = Depends(get_career_document_service),
):
    try:
        return service.get_for_user(current_user.id, document_id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Document not found.") from error


@router.get("/{document_id}/export")
def download_document(
    document_id: int,
    format: str = "pdf",
    current_user: User = Depends(get_current_user),
    service: CareerDocumentService = Depends(get_career_document_service),
):
    try:
        document = service.get_for_user(current_user.id, document_id)
        content, media_type, filename = export_document(document, format)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Document not found.") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return StreamingResponse(
        BytesIO(content),
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.post("", response_model=CareerDocumentResponse, status_code=201)
def create_document(
    request: CareerDocumentCreate,
    current_user: User = Depends(get_current_user),
    service: CareerDocumentService = Depends(get_career_document_service),
):
    try:
        return service.create_for_user(
            current_user.id,
            request.kind,
            request.title,
            request.content,
            request.source_filename,
            request.job_description,
            request.metadata,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{document_id}", response_model=CareerDocumentResponse)
def update_document(
    document_id: int,
    request: CareerDocumentUpdate,
    current_user: User = Depends(get_current_user),
    service: CareerDocumentService = Depends(get_career_document_service),
):
    try:
        return service.update_for_user(
            current_user.id, document_id, request.title, request.content
        )
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Document not found.") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/{document_id}", status_code=204)
def delete_document(
    document_id: int,
    current_user: User = Depends(get_current_user),
    service: CareerDocumentService = Depends(get_career_document_service),
):
    try:
        service.delete_for_user(current_user.id, document_id)
    except DocumentNotFoundError as error:
        raise HTTPException(status_code=404, detail="Document not found.") from error
    return Response(status_code=204)
