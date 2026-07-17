from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


app = FastAPI(
    title="AI Career Assistant API",
    description="AI-powered career analysis platform",
    version="1.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(skills_router)
app.include_router(dashboard_router)
app.include_router(resume_router)
app.include_router(job_match_router)
app.include_router(resume_tailor_router)
app.include_router(cover_letter_router)
app.include_router(analytics_router)
app.include_router(job_search_router)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(profile_router)
app.include_router(documents_router)
@app.get("/")
def home():

    return {
        "message": "AI Career Assistant API is running"
    }
