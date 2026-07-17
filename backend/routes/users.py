from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from backend.models.user import User

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_user_data_service
from backend.services.user_data_service import UserDataService


router = APIRouter(
    tags=["Users"]
)


@router.get("/users/me")
def get_me(
    current_user: User = Depends(get_current_user)
):

    return {
        "id": current_user.id,
        "email": current_user.email,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "created_at": current_user.created_at,
        "is_email_verified": current_user.is_email_verified,
    }


@router.get("/users/me/export")
def export_my_data(
    current_user: User = Depends(get_current_user),
    service: UserDataService = Depends(get_user_data_service),
):
    return JSONResponse(
        content=service.export_for_user(current_user),
        headers={
            "Content-Disposition": (
                'attachment; filename="nexthire-data-export.json"'
            )
        },
    )
