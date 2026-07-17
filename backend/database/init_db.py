from sqlalchemy import inspect, text

from backend.database.database import engine, Base

from backend.models.user import User
from backend.models.profile import Profile
from backend.models.resume_analysis import ResumeAnalysis
from backend.models.career_document import CareerDocument
from backend.models.career_document_revision import CareerDocumentRevision
from backend.models.job_application import JobApplication
from backend.models.ai_usage_event import AIUsageEvent


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

user_columns = {
    column["name"]
    for column in inspect(engine).get_columns("users")
}
user_migrations = {
    "token_version": "INTEGER NOT NULL DEFAULT 0",
    "failed_login_attempts": "INTEGER NOT NULL DEFAULT 0",
    "locked_until": "DATETIME",
    "is_email_verified": "BOOLEAN NOT NULL DEFAULT 0",
}
for name, definition in user_migrations.items():
    if name not in user_columns:
        with engine.begin() as connection:
            connection.execute(text(
                f"ALTER TABLE users ADD COLUMN {name} {definition}"
            ))


print("Database created successfully")
