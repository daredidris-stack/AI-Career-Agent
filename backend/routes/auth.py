from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.models.schemas import (
    RegisterRequest,
    LoginRequest,
    UserResponse,
    TokenResponse,
)

from backend.services.auth_service import AuthService

from backend.dependencies.services import (
    get_auth_service,
)

from backend.exceptions.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
)

router = APIRouter(
    tags=["Authentication"]
)


@router.post(
    "/users/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    request: RegisterRequest,
    service: AuthService = Depends(get_auth_service),
):

    try:

        return service.register_user(
            request.email,
            request.password,
        )

    except UserAlreadyExistsError:

        raise HTTPException(
            status_code=409,
            detail="User already exists",
        )


@router.post(
    "/users/login",
    response_model=TokenResponse,
)
def login(
    request: LoginRequest,
    service: AuthService = Depends(get_auth_service),
):

    try:

        token = service.authenticate_user(
            request.email,
            request.password,
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except InvalidCredentialsError:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


@router.post(
    "/auth/token",
    response_model=TokenResponse,
)
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):

    try:

        token = service.authenticate_user(
            form_data.username,
            form_data.password,
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except InvalidCredentialsError:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )