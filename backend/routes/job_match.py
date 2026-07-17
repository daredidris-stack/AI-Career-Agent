from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_ai_usage_service, get_job_match_service
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.job_match_service import (
    JobMatchError,
    JobMatchService,
    ProfileRequiredError,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


class JobMatchRequest(BaseModel):
    resume: str
    job_description: str


@router.post("/match")
def match_job(
    request: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    service: JobMatchService = Depends(
        get_job_match_service
    ),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "job_match")
    try:
        return service.match_for_user(
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
    except JobMatchError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
