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
