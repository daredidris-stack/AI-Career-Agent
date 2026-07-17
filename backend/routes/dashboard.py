from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_dashboard_service
from backend.models.user import User
from backend.services.dashboard_service import (
    DashboardError,
    DashboardService,
    ProfileRequiredError,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


@router.get("")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    service: DashboardService = Depends(get_dashboard_service),
):
    try:
        return service.get_for_user(current_user)
    except ProfileRequiredError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except DashboardError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
