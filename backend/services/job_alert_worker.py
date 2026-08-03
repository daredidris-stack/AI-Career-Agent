import logging
from typing import Any

from backend.core.settings import JOB_ALERT_BATCH_SIZE
from backend.core.time import utc_now
from backend.services.job_alert_service import JobAlertService
from backend.services.job_library_service import JobLibraryService
from backend.services.job_search_service import (
    JobSearchError,
    JobSearchInputError,
    JobSearchService,
)


logger = logging.getLogger(__name__)


class JobAlertWorker:
    def __init__(
        self,
        library: JobLibraryService,
        search: JobSearchService,
        alerts: JobAlertService,
        batch_size: int = JOB_ALERT_BATCH_SIZE,
    ):
        self.library = library
        self.search = search
        self.alerts = alerts
        self.batch_size = max(1, batch_size)

    def run_due(self) -> dict[str, Any]:
        report = {
            "configured": self.alerts.available,
            "due": 0,
            "baselined": 0,
            "sent": 0,
            "no_new_matches": 0,
            "failed": 0,
        }
        if not self.alerts.available:
            return report

        due_searches = self.library.repository.list_due_searches(
            utc_now(),
            self.batch_size,
        )
        report["due"] = len(due_searches)
        for saved_search, user in due_searches:
            self.alerts.claim_search(saved_search)
            try:
                result = self.search.search_for_user(
                    user_id=user.id,
                    **self.library.search_filters(saved_search),
                    page=1,
                    per_page=50,
                )
                jobs = result.get("jobs", [])
                is_first_run = saved_search.last_run_at is None
                new_jobs = self.library.new_jobs(saved_search, jobs)

                if is_first_run:
                    self.library.record_search_results(saved_search, jobs)
                    self.alerts.complete_search(saved_search)
                    report["baselined"] += 1
                elif not new_jobs:
                    self.library.record_search_results(saved_search, jobs)
                    self.alerts.complete_search(saved_search)
                    report["no_new_matches"] += 1
                elif self.alerts.send_matches(
                    saved_search,
                    user,
                    new_jobs,
                ):
                    self.library.record_search_results(saved_search, jobs)
                    self.alerts.complete_search(saved_search)
                    report["sent"] += 1
                else:
                    report["failed"] += 1
            except (JobSearchError, JobSearchInputError, ValueError) as error:
                logger.warning(
                    "Saved-search email alert failed (%s).",
                    type(error).__name__,
                )
                report["failed"] += 1
        return report
