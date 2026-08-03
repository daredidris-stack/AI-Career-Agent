import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from fastapi import HTTPException

from backend.models.schemas import (
    EmailAlertUnsubscribe,
    SavedJobCreate,
    SavedSearchAlertUpdate,
    SavedSearchCreate,
    SavedSearchFilters,
)
from backend.routes.job_library import (
    acknowledge_saved_search,
    create_saved_search,
    delete_saved_job,
    run_saved_search,
    save_job,
    unsubscribe_from_saved_search_alert,
    update_saved_search_email_alerts,
)
from backend.services.job_alert_service import InvalidUnsubscribeTokenError
from backend.services.job_library_service import JobLibraryItemNotFoundError
from backend.services.job_search_service import JobSearchError


class JobLibraryRouteTests(unittest.TestCase):
    def setUp(self):
        self.user = SimpleNamespace(id=17, is_email_verified=True)

    def test_save_job_passes_authenticated_owner_and_payload(self):
        request = SavedJobCreate(
            title="Platform Engineer",
            company="Example",
            listing_url="https://jobs.example.com/123",
        )
        service = Mock()
        service.save_job.return_value = {"id": 3}

        result = save_job(request, self.user, service)

        self.assertEqual(result, {"id": 3})
        service.save_job.assert_called_once_with(
            17,
            request.model_dump(),
        )

    def test_delete_missing_saved_job_returns_404(self):
        service = Mock()
        service.delete_saved_job.side_effect = JobLibraryItemNotFoundError()

        with self.assertRaises(HTTPException) as context:
            delete_saved_job(9, self.user, service)

        self.assertEqual(context.exception.status_code, 404)

    def test_create_search_passes_validated_filters(self):
        request = SavedSearchCreate(
            name="Remote platform roles",
            filters=SavedSearchFilters(
                keyword="Platform Engineer",
                work_mode="Remote",
            ),
        )
        service = Mock()
        service.create_search.return_value = {"id": 4}

        result = create_saved_search(request, self.user, service)

        self.assertEqual(result, {"id": 4})
        service.create_search.assert_called_once_with(
            17,
            "Remote platform roles",
            request.filters.model_dump(),
        )

    def test_acknowledge_search_passes_authenticated_owner(self):
        service = Mock()
        service.acknowledge_search.return_value = {"id": 4}

        result = acknowledge_saved_search(4, self.user, service)

        self.assertEqual(result, {"id": 4})
        service.acknowledge_search.assert_called_once_with(17, 4)

    def test_update_email_alert_uses_authenticated_user(self):
        request = SavedSearchAlertUpdate(
            enabled=True,
            frequency="weekly",
            timezone="America/Mexico_City",
        )
        service = Mock()
        service.update_preferences.return_value = {"id": 4}

        result = update_saved_search_email_alerts(
            4,
            request,
            self.user,
            service,
        )

        self.assertEqual(result, {"id": 4})
        service.update_preferences.assert_called_once_with(
            self.user,
            4,
            True,
            "weekly",
            "America/Mexico_City",
        )

    def test_invalid_unsubscribe_token_returns_400(self):
        service = Mock()
        service.unsubscribe.side_effect = InvalidUnsubscribeTokenError()

        with self.assertRaises(HTTPException) as context:
            unsubscribe_from_saved_search_alert(
                EmailAlertUnsubscribe(token="x" * 20),
                service,
            )

        self.assertEqual(context.exception.status_code, 400)

    @patch("backend.routes.job_library.AI_JOB_RANKING_ENABLED", False)
    def test_run_search_uses_saved_filters_and_records_results(self):
        library = Mock()
        search = Mock()
        usage = Mock()
        saved_search = SimpleNamespace(id=4)
        filters = {
            "keyword": "Platform Engineer",
            "country": "Worldwide",
            "city": "",
            "industry": "",
            "work_mode": "Remote",
            "employment_type": "",
            "posted_within_days": 7,
            "min_salary": 0,
            "min_score": 0,
        }
        result = {"jobs": [{"title": "SRE"}], "count": 1}
        library.get_search.return_value = saved_search
        library.search_filters.return_value = filters
        library.record_search_results.return_value = {"id": 4}
        search.search_for_user.return_value = result

        response = run_saved_search(
            4,
            self.user,
            library,
            search,
            usage,
        )

        search.search_for_user.assert_called_once_with(
            user_id=17,
            **filters,
            page=1,
            per_page=50,
        )
        library.record_search_results.assert_called_once_with(
            saved_search,
            result["jobs"],
        )
        self.assertEqual(
            response,
            {"saved_search": {"id": 4}, "result": result},
        )

    def test_run_search_provider_error_returns_502(self):
        library = Mock()
        search = Mock()
        library.get_search.return_value = SimpleNamespace(id=4)
        library.search_filters.return_value = {"keyword": "Cloud"}
        search.search_for_user.side_effect = JobSearchError(
            "Job search is temporarily unavailable."
        )

        with self.assertRaises(HTTPException) as context:
            run_saved_search(
                4,
                self.user,
                library,
                search,
                Mock(),
            )

        self.assertEqual(context.exception.status_code, 502)


if __name__ == "__main__":
    unittest.main()
