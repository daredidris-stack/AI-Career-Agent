from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import (
    get_resume_service,
    get_ai_usage_service,
)
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.resume_service import (
    ProfileRequiredError,
    ResumeAnalysisError,
    ResumeService,
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.post("/analyze")
async def analyze_resume_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    resume_service: ResumeService = Depends(
        get_resume_service
    ),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "resume_analysis")
    try:
        return await resume_service.analyze_upload(
            file,
            current_user.id,
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
    except ResumeAnalysisError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
