import time
from typing import Callable, Dict, Tuple
from fastapi import Depends, HTTPException, Request, status

# In-memory storage: { (key, window_start): count }
# We'll use a simple dict and clean up old entries occasionally.
_request_log: Dict[Tuple[str, int], int] = {}
# To avoid unbounded growth, we'll keep a separate set of keys to clean.
# But for simplicity, we'll just let it grow; in production use Redis.
# Since this is a demo, we'll accept the memory tradeoff.

def _get_key(request: Request, prefix: str) -> str:
    """
    Generate a key based on client IP and a prefix (e.g., endpoint type).
    Using X-Forwarded-For if present, else remote address.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        ip = forwarded.split(",")[0].strip()
    else:
        ip = request.client.host if request.client else "unknown"
    return f"{prefix}:{ip}"

def _check_rate_limit(request: Request, prefix: str, limit: int, window_seconds: int = 60) -> None:
    """
    Fixed window rate limiter.
    Raises HTTPException 429 if limit exceeded.
    """
    key = _get_key(request, prefix)
    current_window = int(time.time() // window_seconds)
    log_key = (key, current_window)
    count = _request_log.get(log_key, 0)
    if count >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )
    _request_log[log_key] = count + 1

# Dependency factories
def auth_rate_limit(request: Request):
    """Limit authentication endpoints to 5 attempts per minute."""
    _check_rate_limit(request, "auth", 5, 60)

def job_search_rate_limit(request: Request):
    """Limit job search endpoints to 10 requests per minute."""
    _check_rate_limit(request, "job_search", 10, 60)

def ai_endpoint_rate_limit(request: Request):
    """Limit expensive AI endpoints to 5 requests per minute."""
    _check_rate_limit(request, "ai_endpoint", 5, 60)

def general_rate_limit(request: Request):
    """General rate limit for all endpoints: 100 requests per minute."""
    _check_rate_limit(request, "general", 100, 60)
