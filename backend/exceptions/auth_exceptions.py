class UserAlreadyExistsError(Exception):
    """Raised when attempting to register an existing user."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""