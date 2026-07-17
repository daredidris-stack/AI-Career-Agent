from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_resume_tailor_service
from backend.models.user import User
from backend.services.resume_tailor_service import (
    ProfileRequiredError,
    ResumeTailorError,
    ResumeTailorService,
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.post("/tailor-upload")
async def tailor_resume_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...),
    current_user: User = Depends(get_current_user),
    service: ResumeTailorService = Depends(
        get_resume_tailor_service
    ),
):
    try:
        return await service.tailor_for_user(
            user_id=current_user.id,
            file=file,
            job_description=job_description,
        )
    except ProfileRequiredError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
    except ResumeTailorError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
