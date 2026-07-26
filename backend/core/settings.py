import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env", override=False)


def normalize_database_url(value: str) -> str:
    """Use SQLAlchemy's psycopg 3 driver for hosted PostgreSQL URLs."""
    if value.startswith("postgres://"):
        return value.replace("postgres://", "postgresql+psycopg://", 1)
    if value.startswith("postgresql://"):
        return value.replace("postgresql://", "postgresql+psycopg://", 1)
    return value


DATABASE_URL = normalize_database_url(
    os.getenv("DATABASE_URL", "sqlite:///./career_agent.db")
)

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_HOURS = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_HOURS", "24")
)

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
TURNSTILE_SECRET_KEY = os.getenv("TURNSTILE_SECRET_KEY")
TURNSTILE_ALLOWED_HOSTNAMES = [
    hostname.strip().casefold()
    for hostname in os.getenv("TURNSTILE_ALLOWED_HOSTNAMES", "").split(",")
    if hostname.strip()
]

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
ADZUNA_WORLDWIDE_MARKETS = [
    country.strip().casefold()
    for country in os.getenv(
        "ADZUNA_WORLDWIDE_MARKETS",
        "us,gb,ca,au,de,fr,in,mx",
    ).split(",")
    if country.strip()
]
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY")
THEIRSTACK_API_KEY = os.getenv("THEIRSTACK_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")
FANTASTIC_JOBS_API_KEY = os.getenv("FANTASTIC_JOBS_API_KEY")
FANTASTIC_JOBS_MAX_RESULTS = max(
    1, min(100, int(os.getenv("FANTASTIC_JOBS_MAX_RESULTS", "20")))
)
FANTASTIC_JOBS_CACHE_SECONDS = max(
    60, int(os.getenv("FANTASTIC_JOBS_CACHE_SECONDS", "900"))
)
_fantastic_jobs_time_frame = os.getenv(
    "FANTASTIC_JOBS_TIME_FRAME", "6m"
)
FANTASTIC_JOBS_TIME_FRAME = (
    _fantastic_jobs_time_frame
    if _fantastic_jobs_time_frame in {"1h", "24h", "7d", "6m"}
    else "6m"
)
JOB_INGESTION_QUERIES = [
    value.strip()
    for value in os.getenv("JOB_INGESTION_QUERIES", "").split(",")
    if value.strip()
]
JOB_INGESTION_RESULTS_PER_TARGET = max(
    1, min(100, int(os.getenv("JOB_INGESTION_RESULTS_PER_TARGET", "20")))
)
JOB_INGESTION_INTERVAL_SECONDS = max(
    3600, int(os.getenv("JOB_INGESTION_INTERVAL_SECONDS", "86400"))
)
JOB_INGESTION_RETRY_SECONDS = max(
    300, int(os.getenv("JOB_INGESTION_RETRY_SECONDS", "3600"))
)
JOB_INGESTION_POLL_SECONDS = max(
    60, int(os.getenv("JOB_INGESTION_POLL_SECONDS", "900"))
)
JOB_LISTING_STALE_DAYS = max(
    1, int(os.getenv("JOB_LISTING_STALE_DAYS", "45"))
)
USAJOBS_API_KEY = os.getenv("USAJOBS_API_KEY")
USAJOBS_USER_AGENT = os.getenv("USAJOBS_USER_AGENT")
GREENHOUSE_JOB_BOARDS = [
    value.strip()
    for value in os.getenv("GREENHOUSE_JOB_BOARDS", "").split(",")
    if value.strip()
]
LEVER_JOB_SITES = [
    value.strip()
    for value in os.getenv("LEVER_JOB_SITES", "").split(",")
    if value.strip()
]
ASHBY_JOB_BOARDS = [
    value.strip()
    for value in os.getenv("ASHBY_JOB_BOARDS", "").split(",")
    if value.strip()
]
DIRECT_EMPLOYER_JOB_SOURCES = {
    value.strip().casefold()
    for value in os.getenv("DIRECT_EMPLOYER_JOB_SOURCES", "").split(",")
    if value.strip()
}

AI_MODEL = os.getenv("AI_MODEL", "qwen3:8b")
AI_REQUEST_TIMEOUT_SECONDS = float(
    os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "45")
)
AI_MAX_RETRIES = max(0, int(os.getenv("AI_MAX_RETRIES", "1")))
AI_MAX_PROMPT_CHARACTERS = max(
    1000, int(os.getenv("AI_MAX_PROMPT_CHARACTERS", "30000"))
)
AI_JOB_RANKING_ENABLED = (
    os.getenv("AI_JOB_RANKING_ENABLED", "false").casefold() == "true"
)
AI_REQUESTS_PER_HOUR = max(
    1, int(os.getenv("AI_REQUESTS_PER_HOUR", "20"))
)
AI_REQUESTS_PER_DAY = max(
    AI_REQUESTS_PER_HOUR,
    int(os.getenv("AI_REQUESTS_PER_DAY", "100")),
)
AI_PRO_REQUESTS_PER_HOUR = max(
    AI_REQUESTS_PER_HOUR,
    int(os.getenv("AI_PRO_REQUESTS_PER_HOUR", "100")),
)
AI_PRO_REQUESTS_PER_DAY = max(
    AI_PRO_REQUESTS_PER_HOUR,
    int(os.getenv("AI_PRO_REQUESTS_PER_DAY", "1000")),
)
MAX_RESUME_UPLOAD_BYTES = max(
    1024, int(os.getenv("MAX_RESUME_UPLOAD_BYTES", str(5 * 1024 * 1024)))
)

APP_ENV = os.getenv("APP_ENV", "development")
APP_RELEASE = os.getenv("APP_RELEASE", "development")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LEGAL_TERMS_VERSION = os.getenv("LEGAL_TERMS_VERSION", "2026-07-17")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ALLOWED_ORIGINS",
        (
            "http://localhost:5173,http://localhost:5174,"
            "http://127.0.0.1:5173,http://127.0.0.1:5174"
        ),
    ).split(",")
    if origin.strip()
]
REQUIRE_EMAIL_VERIFICATION = (
    os.getenv("REQUIRE_EMAIL_VERIFICATION", "false").casefold() == "true"
)
SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL")
SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").casefold() == "true"
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")
STRIPE_PRO_PRICE_ID = os.getenv("STRIPE_PRO_PRICE_ID")


def require_jwt_secret() -> str:
    if not JWT_SECRET_KEY:
        raise RuntimeError(
            "JWT_SECRET_KEY must be configured in the environment."
        )

    return JWT_SECRET_KEY
