from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_ai_usage_service, get_job_search_service
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
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
    keyword: str | None = None,
    country: str | None = None,
    city: str | None = None,
    industry: str | None = None,
    work_mode: str | None = None,
    employment_type: str | None = None,
    posted_within_days: int = 0,
    min_salary: int = 0,
    min_score: int = 0,
    page: int = 1,
    per_page: int = 20,
    current_user: User = Depends(get_current_user),
    service: JobSearchService = Depends(
        get_job_search_service
    ),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "job_search_ranking")
    try:
        return service.search_for_user(
            user_id=current_user.id,
            keyword=keyword,
            country=country,
            city=city,
            industry=industry,
            work_mode=work_mode,
            employment_type=employment_type,
            posted_within_days=posted_within_days,
            min_salary=min_salary,
            min_score=min_score,
            page=page,
            per_page=per_page,
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
