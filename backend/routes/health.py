from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.orm import Session

from backend.core.settings import APP_ENV, APP_RELEASE, DATABASE_URL
from backend.database.database import get_db


router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def liveness():
    return {"status": "ok", "release": APP_RELEASE}


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    checks = {
        "database": "ok",
        "production_database": (
            "ok"
            if APP_ENV != "production" or not DATABASE_URL.startswith("sqlite")
            else "misconfigured"
        ),
    }
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        checks["database"] = "unavailable"

    ready = all(value == "ok" for value in checks.values())
    payload = {
        "status": "ready" if ready else "not_ready",
        "release": APP_RELEASE,
        "checks": checks,
    }
    return payload if ready else JSONResponse(status_code=503, content=payload)
