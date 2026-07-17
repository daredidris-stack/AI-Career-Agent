from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_cover_letter_service
from backend.models.user import User
from backend.services.cover_letter_service import (
    CoverLetterError,
    CoverLetterService,
    ProfileRequiredError,
)


router = APIRouter(
    tags=["Cover Letter"],
)


class CoverLetterRequest(BaseModel):
    resume: str
    job_description: str


@router.post("/cover-letter")
def generate_cover_letter(
    request: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
    service: CoverLetterService = Depends(
        get_cover_letter_service
    ),
):
    try:
        return service.generate_for_user(
            user_id=current_user.id,
            resume=request.resume,
            job_description=request.job_description,
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
    except CoverLetterError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
