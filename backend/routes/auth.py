from fastapi import APIRouter, Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from backend.models.schemas import (
    RegisterRequest,
    LoginRequest,
    GoogleLoginRequest,
    UserResponse,
    TokenResponse,
    DeleteAccountRequest,
    EmailRequest,
    MessageResponse,
    PasswordResetRequest,
    TokenConfirmationRequest,
)

from backend.services.auth_service import AuthService

from backend.dependencies.services import (
    get_auth_service,
    get_turnstile_service,
    get_google_identity_service,
)
from backend.dependencies.auth import get_current_user
from backend.models.user import User

from backend.exceptions.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    LoginLockedError,
    EmailNotVerifiedError,
    InvalidActionTokenError,
    GoogleAccountConflictError,
)
from backend.services.google_identity_service import (
    GoogleIdentityError,
    GoogleIdentityNotConfiguredError,
    GoogleIdentityService,
    GoogleIdentityUnavailableError,
)
from backend.services.turnstile_service import (
    TurnstileService,
    TurnstileUnavailableError,
    TurnstileVerificationError,
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
    turnstile: TurnstileService = Depends(get_turnstile_service),
):

    _verify_turnstile(turnstile, request.turnstile_token)

    try:

        token = service.authenticate_user(
            request.email,
            request.password,
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except LoginLockedError:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again in 15 minutes.",
            headers={"Retry-After": "900"},
        )
    except EmailNotVerifiedError:
        raise HTTPException(
            status_code=403,
            detail="Verify your email before signing in.",
        )
    except InvalidCredentialsError:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


@router.post(
    "/auth/google",
    response_model=TokenResponse,
)
def google_login(
    request: GoogleLoginRequest,
    service: AuthService = Depends(get_auth_service),
    google_identity: GoogleIdentityService = Depends(
        get_google_identity_service
    ),
):
    try:
        identity = google_identity.verify(request.credential)
        token = service.authenticate_google(identity)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )
    except GoogleIdentityNotConfiguredError:
        raise HTTPException(
            status_code=503,
            detail="Google sign-in is not configured.",
        ) from None
    except GoogleIdentityUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Google sign-in is temporarily unavailable.",
        ) from None
    except (GoogleIdentityError, GoogleAccountConflictError):
        raise HTTPException(
            status_code=401,
            detail="Google sign-in could not be verified.",
        ) from None


@router.post(
    "/auth/token",
    response_model=TokenResponse,
)
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
    turnstile: TurnstileService = Depends(get_turnstile_service),
    turnstile_token: str | None = Header(
        default=None,
        alias="X-Turnstile-Token",
    ),
):

    _verify_turnstile(turnstile, turnstile_token)

    try:

        token = service.authenticate_user(
            form_data.username,
            form_data.password,
        )

        return TokenResponse(
            access_token=token,
            token_type="bearer",
        )

    except LoginLockedError:
        raise HTTPException(
            status_code=429,
            detail="Too many failed login attempts. Try again in 15 minutes.",
            headers={"Retry-After": "900"},
        )
    except EmailNotVerifiedError:
        raise HTTPException(
            status_code=403,
            detail="Verify your email before signing in.",
        )
    except InvalidCredentialsError:

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )


def _verify_turnstile(
    turnstile: TurnstileService,
    token: str | None,
) -> None:
    try:
        turnstile.verify(token, expected_action="login")
    except TurnstileVerificationError:
        raise HTTPException(
            status_code=400,
            detail="Security verification failed. Please try again.",
        ) from None
    except TurnstileUnavailableError:
        raise HTTPException(
            status_code=503,
            detail="Security verification is temporarily unavailable.",
        ) from None


@router.delete("/users/me", status_code=204)
def delete_account(
    request: DeleteAccountRequest,
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
):
    try:
        service.delete_account(current_user, request.password)
    except InvalidCredentialsError:
        raise HTTPException(status_code=401, detail="Invalid credentials")


@router.post("/auth/verification/request", response_model=MessageResponse)
def request_verification(
    request: EmailRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.send_verification(request.email)
    return MessageResponse(
        message="If the account exists, a verification email has been sent."
    )


@router.post("/auth/verification/confirm", response_model=MessageResponse)
def confirm_verification(
    request: TokenConfirmationRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        service.confirm_verification(request.token)
    except InvalidActionTokenError:
        raise HTTPException(
            status_code=400,
            detail="The verification link is invalid or expired.",
        )
    return MessageResponse(message="Email verified successfully.")


@router.post("/auth/password/forgot", response_model=MessageResponse)
def forgot_password(
    request: EmailRequest,
    service: AuthService = Depends(get_auth_service),
):
    service.send_password_reset(request.email)
    return MessageResponse(
        message="If the account exists, a password reset email has been sent."
    )


@router.post("/auth/password/reset", response_model=MessageResponse)
def reset_password(
    request: PasswordResetRequest,
    service: AuthService = Depends(get_auth_service),
):
    try:
        service.reset_password(request.token, request.new_password)
    except InvalidActionTokenError:
        raise HTTPException(
            status_code=400,
            detail="The password reset link is invalid or expired.",
        )
    return MessageResponse(message="Password reset successfully.")
