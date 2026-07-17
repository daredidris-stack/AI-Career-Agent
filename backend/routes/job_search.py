from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_job_search_service
from backend.models.user import User
from backend.services.job_search_service import (
    JobSearchError,
    JobSearchService,
    ProfileRequiredError,
)


router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
)


@router.get("/search")
def search_jobs(
    keyword: str,
    location: str = "Remote",
    experience: str = "",
    min_score: int = 0,
    ai_rank: bool = True,
    current_user: User = Depends(get_current_user),
    service: JobSearchService = Depends(
        get_job_search_service
    ),
):
    try:
        return service.search_for_user(
            user_id=current_user.id,
            keyword=keyword,
            location=location,
            experience=experience,
            min_score=min_score,
            ai_rank=ai_rank,
        )
    except ProfileRequiredError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except JobSearchError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
