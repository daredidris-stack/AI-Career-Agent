from backend.database.database import engine, Base

from backend.models.user import User
from backend.models.profile import Profile
from backend.models.resume_analysis import ResumeAnalysis


print("Creating database...")


Base.metadata.create_all(
    bind=engine
)


print("Database created successfully")
