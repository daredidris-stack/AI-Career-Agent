from backend.auth.hashing import (
    hash_password,
    verify_password,
)

from backend.auth.jwt_handler import (
    create_access_token,
)

from backend.repositories.user_repository import UserRepository

from backend.exceptions.auth_exceptions import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
)


class AuthService:

    def __init__(
        self,
        repo: UserRepository,
    ):
        self.repo = repo


    def register_user(
        self,
        email: str,
        password: str,
    ):

        existing = self.repo.get_by_email(email)

        if existing:
            raise UserAlreadyExistsError()

        return self.repo.create_user(
            email=email,
            password_hash=hash_password(password),
        )


    def authenticate_user(
        self,
        email: str,
        password: str,
    ):

        user = self.repo.get_by_email(email)

        if not user:
            raise InvalidCredentialsError()

        if not verify_password(
            password,
            user.password_hash,
        ):
            raise InvalidCredentialsError()

        return create_access_token(
            {
                "user_id": user.id,
                "email": user.email,
            }
        )