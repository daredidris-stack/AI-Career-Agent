class UserAlreadyExistsError(Exception):
    """Raised when attempting to register an existing user."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials are invalid."""


class LoginLockedError(Exception):
    """Raised when repeated failed logins temporarily lock an account."""


class EmailNotVerifiedError(Exception):
    """Raised when verification is required before login."""


class InvalidActionTokenError(Exception):
    """Raised when a verification or reset token is invalid or expired."""


class UserNotFoundError(Exception):
    """Raised when a user cannot be found."""
