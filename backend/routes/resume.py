from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import (
    get_profile_service,
    get_resume_service,
)
from backend.models.user import User
from backend.services.profile_service import ProfileService
from backend.services.resume_service import ResumeService


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


@router.post("/analyze")
async def analyze_resume_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    profile_service: ProfileService = Depends(
        get_profile_service
    ),
    resume_service: ResumeService = Depends(
        get_resume_service
    ),
):
    profile = profile_service.get_profile(current_user.id)

    if not profile:
        raise HTTPException(
            status_code=404,
            detail=(
                "Create your profile before analyzing "
                "a resume."
            ),
        )

    try:
        return await resume_service.analyze_upload(
            file,
            profile,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        ) from error
