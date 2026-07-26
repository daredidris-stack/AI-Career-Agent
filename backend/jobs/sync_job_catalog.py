import argparse
import logging
import time

from backend.core.settings import (
    FANTASTIC_JOBS_API_KEY,
    JOB_INGESTION_POLL_SECONDS,
)
from backend.database.database import SessionLocal
from backend.repositories.job_listing_repository import JobListingRepository
from backend.repositories.profile_repository import ProfileRepository
from backend.services.job_ingestion_service import JobIngestionService


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_once(force: bool = False) -> dict:
    if not FANTASTIC_JOBS_API_KEY:
        raise RuntimeError(
            "FANTASTIC_JOBS_API_KEY is required for job ingestion."
        )
    db = SessionLocal()
    try:
        service = JobIngestionService(
            JobListingRepository(db),
            ProfileRepository(db),
        )
        return service.run_once(force=force)
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Synchronize profile-targeted jobs into the local database."
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Keep polling and run targets when their next sync is due.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ignore next-sync timestamps for the first run.",
    )
    args = parser.parse_args()

    try:
        while True:
            try:
                report = run_once(force=args.force)
            except Exception as error:
                if not args.watch:
                    raise
                logger.warning(
                    "Job ingestion cycle failed; retrying after the poll "
                    "interval (%s)",
                    type(error).__name__,
                )
            else:
                logger.info("Job ingestion report: %s", report)
            args.force = False
            if not args.watch:
                return
            time.sleep(JOB_INGESTION_POLL_SECONDS)
    except KeyboardInterrupt:
        if not args.watch:
            raise
        logger.info("Job ingestion worker stopped.")


if __name__ == "__main__":
    main()
