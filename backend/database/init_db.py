from sqlalchemy import inspect, text

from backend.database.database import engine, Base

from backend.models.user import User
from backend.models.profile import Profile
from backend.models.resume_analysis import ResumeAnalysis


print("Creating database...")


Base.metadata.create_all(
    bind=engine
)


columns = {
    column["name"]
    for column in inspect(engine).get_columns("resume_analyses")
}

if "extracted_skills" not in columns:
    with engine.begin() as connection:
        connection.execute(text(
            "ALTER TABLE resume_analyses "
            "ADD COLUMN extracted_skills TEXT "
            "NOT NULL DEFAULT '[]'"
        ))


print("Database created successfully")
