from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException, status
from fastapi import Depends

limiter = Limiter(key_func=get_remote_address)

def _check_rate_limit(request: Request, limit_string: str):
    """
    Dependency that checks the rate limit for the current request.
    If the limit is exceeded, raises HTTPException 429.
    """
    try:
        limiter.hit(limit_string, request)
    except RateLimitExceeded:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )

# Convenience dependencies for common limits
def auth_rate_limit(request: Request):
    """Limit authentication endpoints to 5 attempts per minute per IP."""
    return _check_rate_limit(request, "5/minute")

def job_search_rate_limit(request: Request):
    """Limit job search endpoints to 10 requests per minute per IP."""
    return _check_rate_limit(request, "10/minute")

def ai_endpoint_rate_limit(request: Request):
    """Limit expensive AI endpoints to 5 requests per minute per IP."""
    return _check_rate_limit(request, "5/minute")

def general_rate_limit(request: Request):
    """General rate limit for all endpoints: 100 requests per minute per IP."""
    return _check_rate_limit(request, "100/minute")
