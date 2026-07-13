from fastapi import FastAPI

from backend.routes.skills import router as skills_router


app = FastAPI(
    title="AI Career Assistant API",
    description="AI-powered career analysis platform",
    version="1.0"
)


app.include_router(skills_router)


@app.get("/")
def home():
    return {
        "message": "AI Career Assistant API is running"
    }