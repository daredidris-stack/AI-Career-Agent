from fastapi import Depends
from sqlalchemy.orm import Session

from backend.database.database import get_db

from backend.repositories.user_repository import (
    UserRepository,
)

from backend.repositories.profile_repository import (
    ProfileRepository,
)

from backend.repositories.job_catalog_repository import (
    JobCatalogRepository,
)

from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)
from backend.repositories.career_document_repository import (
    CareerDocumentRepository,
)
from backend.repositories.job_application_repository import (
    JobApplicationRepository,
)
from backend.repositories.ai_usage_repository import AIUsageRepository


def get_user_repository(
    db: Session = Depends(get_db),
) -> UserRepository:

    return UserRepository(db)



def get_profile_repository(
    db: Session = Depends(get_db),
) -> ProfileRepository:

    return ProfileRepository(db)


def get_job_catalog_repository():
    return JobCatalogRepository()


def get_resume_analysis_repository(
    db: Session = Depends(get_db),
) -> ResumeAnalysisRepository:
    return ResumeAnalysisRepository(db)


def get_career_document_repository(
    db: Session = Depends(get_db),
) -> CareerDocumentRepository:
    return CareerDocumentRepository(db)


def get_job_application_repository(
    db: Session = Depends(get_db),
) -> JobApplicationRepository:
    return JobApplicationRepository(db)


def get_ai_usage_repository(
    db: Session = Depends(get_db),
) -> AIUsageRepository:
    return AIUsageRepository(db)
