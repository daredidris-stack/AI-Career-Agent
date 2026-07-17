from fastapi import APIRouter, Depends

from backend.models.user import User

from backend.dependencies.auth import get_current_user


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
