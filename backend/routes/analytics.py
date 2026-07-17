from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_analytics_service
from backend.models.user import User
from backend.services.analytics_service import (
    AnalyticsError,
    AnalyticsService,
    ProfileRequiredError,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)


@router.get("")
def get_analytics(
    current_user: User = Depends(get_current_user),
    service: AnalyticsService = Depends(get_analytics_service),
):
    try:
        return service.get_for_user(current_user.id)
    except ProfileRequiredError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except AnalyticsError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
