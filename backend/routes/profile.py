from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)

from backend.models.user import User

from backend.models.schemas import (
    ProfileCreate,
    ProfileResponse,
)

from backend.services.profile_service import (
    ProfileService,
)

from backend.dependencies.services import (
    get_profile_service,
)

from backend.dependencies.auth import (
    get_current_user,
)


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)



@router.get(
    "",
    response_model=ProfileResponse,
)
def get_profile(
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):

    profile = service.get_profile(
        current_user.id
    )


    if not profile:
        raise HTTPException(
            status_code=404,
            detail="Profile not found",
        )


    return profile



@router.post(
    "",
    response_model=ProfileResponse,
    status_code=201,
)
def create_profile(
    request: ProfileCreate,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):

    return service.create_profile(
        current_user.id,
        request.model_dump(),
    )



@router.put(
    "",
    response_model=ProfileResponse,
)
def update_profile(
    request: ProfileCreate,
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):

    return service.update_profile(
        current_user.id,
        request.model_dump(),
    )



@router.delete(
    "",
)
def delete_profile(
    current_user: User = Depends(
        get_current_user
    ),
    service: ProfileService = Depends(
        get_profile_service
    ),
):

    service.delete_profile(
        current_user.id
    )


    return {
        "message": "Profile deleted"
    }