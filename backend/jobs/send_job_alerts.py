import logging

from backend.database.database import SessionLocal
from backend.repositories.job_library_repository import JobLibraryRepository
from backend.repositories.job_listing_repository import JobListingRepository
from backend.repositories.profile_repository import ProfileRepository
from backend.repositories.resume_analysis_repository import (
    ResumeAnalysisRepository,
)
from backend.services.job_alert_service import JobAlertService
from backend.services.job_alert_worker import JobAlertWorker
from backend.services.job_library_service import JobLibraryService
from backend.services.job_search_service import JobSearchService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_once() -> dict:
    db = SessionLocal()
    try:
        library_repository = JobLibraryRepository(db)
        library = JobLibraryService(library_repository)
        search = JobSearchService(
            ProfileRepository(db),
            ResumeAnalysisRepository(db),
            enable_ai_ranking=False,
            job_listing_repository=JobListingRepository(db),
        )
        alerts = JobAlertService(library_repository)
        return JobAlertWorker(library, search, alerts).run_due()
    finally:
        db.close()


def main() -> None:
    report = run_once()
    logger.info("Job alert report: %s", report)


if __name__ == "__main__":
    main()
