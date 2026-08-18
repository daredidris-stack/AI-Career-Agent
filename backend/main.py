from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from backend.core.security_middleware import SecurityHeadersMiddleware
from fastapi import Depends

from backend.routes.skills import router as skills_router
from backend.routes.dashboard import router as dashboard_router
from backend.routes.resume import router as resume_router
from backend.routes.job_match import router as job_match_router
from backend.routes.resume_tailor import router as resume_tailor_router
from backend.routes.cover_letter import router as cover_letter_router
from backend.routes.analytics import router as analytics_router
from backend.routes.job_search import router as job_search_router
from backend.routes.auth import router as auth_router
from backend.routes.users import router as users_router
from backend.routes.profile import router as profile_router
from backend.routes.documents import router as documents_router
from backend.routes.applications import router as applications_router
from backend.routes.health import router as health_router
from backend.routes.billing import router as billing_router
from backend.routes.job_library import router as job_library_router
from backend.routes.support import router as support_router
from backend.routes.interview_practice import router as interview_practice_router
from backend.services.ai_usage_service import AIUsageLimitError
from backend.core.logging import log_request
from backend.core.settings import CORS_ALLOWED_ORIGINS
from backend.core.simple_rate_limiter import auth_rate_limit, job_search_rate_limit, ai_endpoint_rate_limit


app = FastAPI(
    title="AI Career Assistant API",
    description="AI-powered career analysis platform",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(SecurityHeadersMiddleware)
app.middleware("http")(log_request)


@app.exception_handler(AIUsageLimitError)
def ai_usage_limit_handler(
    _request: Request, error: AIUsageLimitError
):
    return JSONResponse(status_code=429, content={"detail": str(error)})


app.include_router(skills_router, dependencies=[Depends(ai_endpoint_rate_limit)])
app.include_router(dashboard_router)
app.include_router(resume_router, dependencies=[Depends(ai_endpoint_rate_limit)])
app.include_router(job_match_router)
app.include_router(resume_tailor_router)
app.include_router(cover_letter_router, dependencies=[Depends(ai_endpoint_rate_limit)])
app.include_router(analytics_router)
app.include_router(job_search_router, dependencies=[Depends(job_search_rate_limit)])
app.include_router(auth_router, dependencies=[Depends(auth_rate_limit)])
app.include_router(users_router)
app.include_router(profile_router)
app.include_router(documents_router)
app.include_router(applications_router)
app.include_router(health_router)
app.include_router(billing_router)
app.include_router(job_library_router)
app.include_router(support_router)
app.include_router(interview_practice_router)


@app.get("/")
def home():

    return {
        "message": "AI Career Assistant API is running"
    }
