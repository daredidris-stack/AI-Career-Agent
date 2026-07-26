from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)

from backend.models.user import User

from backend.models.schemas import (
    ProfileAutofillResponse,
    ProfileCreate,
    ProfileResponse,
)

from backend.services.profile_service import (
    ProfileService,
)

from backend.dependencies.services import (
    get_ai_usage_service,
    get_profile_autofill_service,
    get_profile_service,
)

from backend.dependencies.auth import (
    get_current_user,
)
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.profile_autofill_service import (
    ProfileAutofillError,
    ProfileAutofillService,
)


router = APIRouter(
    prefix="/profile",
    tags=["Profile"],
)


@router.post(
    "/autofill",
    response_model=ProfileAutofillResponse,
)
async def autofill_profile(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    service: ProfileAutofillService = Depends(get_profile_autofill_service),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "profile_autofill")
    try:
        return await service.autofill_upload(file)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except ProfileAutofillError as error:
        raise HTTPException(status_code=502, detail=str(error)) from error



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
