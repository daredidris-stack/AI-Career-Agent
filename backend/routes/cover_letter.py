from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_ai_usage_service, get_cover_letter_service
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.cover_letter_service import (
    CoverLetterError,
    CoverLetterService,
    ProfileRequiredError,
)


router = APIRouter(
    tags=["Cover Letter"],
)


class CoverLetterRequest(BaseModel):
    resume: str | None = None
    job_description: str


@router.post("/cover-letter")
def generate_cover_letter(
    request: CoverLetterRequest,
    current_user: User = Depends(get_current_user),
    service: CoverLetterService = Depends(
        get_cover_letter_service
    ),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "cover_letter")
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
