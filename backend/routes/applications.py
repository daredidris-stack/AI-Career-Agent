from fastapi import APIRouter, Depends, HTTPException, Response

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_job_application_service
from backend.models.schemas import (
    JobApplicationCreate,
    JobApplicationResponse,
    JobApplicationUpdate,
)
from backend.models.user import User
from backend.services.job_application_service import (
    ApplicationNotFoundError,
    JobApplicationService,
)


router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get("", response_model=list[JobApplicationResponse])
def list_applications(
    status: str | None = None,
    current_user: User = Depends(get_current_user),
    service: JobApplicationService = Depends(get_job_application_service),
):
    try:
        return service.list_for_user(current_user.id, status)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("", response_model=JobApplicationResponse, status_code=201)
def create_application(
    request: JobApplicationCreate,
    current_user: User = Depends(get_current_user),
    service: JobApplicationService = Depends(get_job_application_service),
):
    try:
        return service.create_for_user(
            current_user.id, request.model_dump()
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.put("/{application_id}", response_model=JobApplicationResponse)
def update_application(
    application_id: int,
    request: JobApplicationUpdate,
    current_user: User = Depends(get_current_user),
    service: JobApplicationService = Depends(get_job_application_service),
):
    try:
        return service.update_for_user(
            current_user.id, application_id, request.model_dump()
        )
    except ApplicationNotFoundError as error:
        raise HTTPException(status_code=404, detail="Application not found.") from error
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.delete("/{application_id}", status_code=204)
def delete_application(
    application_id: int,
    current_user: User = Depends(get_current_user),
    service: JobApplicationService = Depends(get_job_application_service),
):
    try:
        service.delete_for_user(current_user.id, application_id)
    except ApplicationNotFoundError as error:
        raise HTTPException(status_code=404, detail="Application not found.") from error
    return Response(status_code=204)
