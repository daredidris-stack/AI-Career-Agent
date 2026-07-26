import unittest
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.job_search_service import (
    JobSearchInputError,
    JobSearchError,
    JobSearchService,
)
from backend.services.job_aggregator import AggregatedJobs


class JobSearchServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            technical_skills="AWS, Python",
            years_experience=4,
            current_role="Technician",
            target_role="Cloud Engineer",
            professional_summary="Infrastructure operations",
            city="Mexico City",
            country="Mexico",
            preferred_work_mode="Remote",
        )
        self.repository = Mock()
        self.repository.get_by_user_id.return_value = self.profile
        self.resume_repository = Mock()
        self.resume_repository.get_latest_skills_by_user_id.return_value = [
            "Linux",
            "Terraform",
        ]

    def test_authenticated_search_uses_users_database_profile(self):
        aggregator = Mock(
            return_value=[{"title": "Cloud Engineer"}]
        )
        ranker = Mock(
            return_value=[
                {
                    "title": "Cloud Engineer",
                    "analysis": {"match_score": 90},
                }
            ]
        )
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            ranker,
        )

        result = service.search_for_user(
            user_id=42,
            keyword="cloud",
            min_score=80,
        )

        self.repository.get_by_user_id.assert_called_once_with(42)
        aggregator.assert_called_once_with(
            "cloud", "Worldwide", "", 1, 50
        )
        candidate_profile = ranker.call_args.args[0]
        self.assertEqual(
            candidate_profile["technical_skills"],
            ["AWS", "Python", "Linux", "Terraform"],
        )
        self.assertEqual(
            ranker.call_args.args[1],
            [{"title": "Cloud Engineer"}],
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["jobs"][0]["analysis"]["match_score"], 90)

    def test_missing_profile_can_search_with_entered_filters(self):
        self.repository.get_by_user_id.return_value = None
        aggregator = Mock(return_value=[{"title": "Cloud Engineer"}])
        ranker = Mock(side_effect=lambda _profile, jobs: jobs)
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            ranker,
        )

        result = service.search_for_user(
            42,
            keyword="Cloud Engineer",
            country="Canada",
            city="Toronto",
        )

        aggregator.assert_called_once_with(
            "Cloud Engineer", "Toronto, Canada", "", 1, 50
        )
        self.assertEqual(result["count"], 1)
        self.assertEqual(
            ranker.call_args.args[0]["technical_skills"],
            ["Linux", "Terraform"],
        )

    def test_missing_profile_and_keyword_returns_input_error(self):
        self.repository.get_by_user_id.return_value = None
        aggregator = Mock()
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(),
        )

        with self.assertRaises(JobSearchInputError):
            service.search_for_user(42)

        aggregator.assert_not_called()

    def test_provider_failure_returns_service_error(self):
        aggregator = Mock(
            side_effect=RuntimeError("provider unavailable")
        )
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(),
        )

        with self.assertRaises(JobSearchError):
            service.search_for_user(42, "cloud")

    def test_ranking_failure_returns_service_error(self):
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            Mock(return_value=[]),
            Mock(side_effect=RuntimeError("LLM unavailable")),
        )

        with self.assertRaises(JobSearchError):
            service.search_for_user(42, "cloud")

    def test_defaults_search_to_profile_role_worldwide(self):
        aggregator = Mock(return_value=[])
        ranker = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            ranker,
        )

        result = service.search_for_user(42)

        aggregator.assert_called_once_with(
            "Cloud Engineer",
            "Worldwide",
            "",
            1,
            50,
        )
        self.assertEqual(result["filters"]["keyword"], "Cloud Engineer")
        self.assertEqual(result["filters"]["location"], "Worldwide")
        self.assertEqual(result["filters"]["country"], "Worldwide")
        self.assertEqual(result["filters"]["city"], "")

    def test_does_not_limit_default_search_to_profile_location(self):
        self.profile.preferred_work_mode = "Hybrid"
        aggregator = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(return_value=[]),
        )

        service.search_for_user(42)

        aggregator.assert_called_once_with(
            "Cloud Engineer",
            "Worldwide",
            "",
            1,
            50,
        )

    def test_search_filters_override_profile_defaults(self):
        aggregator = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(return_value=[]),
        )

        result = service.search_for_user(
            42,
            keyword="Platform Engineer",
            country="Canada",
            city="Toronto",
            industry="Finance",
            work_mode="Hybrid",
        )

        aggregator.assert_called_once_with(
            "Platform Engineer",
            "Toronto, Canada",
            "Finance",
            1,
            50,
        )
        self.assertEqual(result["filters"]["industry"], "Finance")

    def test_worldwide_search_does_not_include_profile_city(self):
        aggregator = Mock(return_value=[])
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(return_value=[]),
        )

        service.search_for_user(
            42,
            country="Worldwide",
            work_mode="Hybrid",
        )

        aggregator.assert_called_once_with(
            "Cloud Engineer",
            "Worldwide",
            "",
            1,
            50,
        )

    def test_only_top_five_candidates_are_ai_ranked(self):
        jobs = [
            {"title": f"Engineer {index}", "description": "AWS"}
            for index in range(8)
        ]
        ranker = Mock(
            side_effect=lambda _profile, candidates: candidates
        )
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            Mock(return_value=jobs),
            ranker,
        )

        result = service.search_for_user(42, per_page=20)

        self.assertEqual(len(ranker.call_args.args[1]), 5)
        self.assertEqual(result["count"], 8)
        self.assertIsNone(result["jobs"][5]["analysis"]["match_score"])

    def test_returns_provider_status_from_aggregator(self):
        jobs = AggregatedJobs(
            [{"title": "Cloud Engineer"}],
            [{"name": "Himalayas", "status": "active", "count": 1}],
        )
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            Mock(return_value=jobs),
            Mock(return_value=[{"title": "Cloud Engineer"}]),
        )

        result = service.search_for_user(42)

        self.assertEqual(result["providers"], jobs.provider_status)

    def test_filters_listing_metadata_before_ai_ranking(self):
        now = datetime.now(timezone.utc)
        jobs = [
            {"title": "Recent", "job_type": "Full Time", "salary_min": 90000, "updated": now.isoformat()},
            {"title": "Old", "job_type": "Full Time", "salary_min": 90000, "updated": (now - timedelta(days=60)).isoformat()},
            {"title": "Contract", "job_type": "Contract", "salary_min": 120000, "updated": now.isoformat()},
        ]
        ranker = Mock(side_effect=lambda _profile, candidates: candidates)
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            Mock(return_value=jobs),
            ranker,
        )

        result = service.search_for_user(
            42,
            employment_type="Full Time",
            posted_within_days=30,
            min_salary=80000,
        )

        self.assertEqual([job["title"] for job in result["jobs"]], ["Recent"])

    def test_stored_jobs_prevent_repeat_live_provider_calls(self):
        aggregator = Mock()
        listing_repository = Mock()
        listing_repository.search.return_value = [{
            "title": "Registered Nurse",
            "company": "Example Health",
            "source": "Employer index",
            "source_homepage": "https://fantastic.jobs/",
            "source_api_page": "https://developer.fantastic.jobs/",
            "cached": True,
        }]
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(side_effect=lambda _profile, jobs: jobs),
            job_listing_repository=listing_repository,
        )

        result = service.search_for_user(42, keyword="Registered Nurse")

        aggregator.assert_not_called()
        listing_repository.upsert_many.assert_not_called()
        self.assertTrue(result["jobs"][0]["cached"])
        self.assertEqual(result["providers"], [{
            "name": "Employer index",
            "status": "active",
            "count": 1,
            "homepage": "https://fantastic.jobs/",
            "api_page": "https://developer.fantastic.jobs/",
            "cached": True,
        }])

    def test_live_fallback_populates_persistent_listing_store(self):
        live_jobs = AggregatedJobs(
            [{
                "title": "Accountant",
                "company": "Example Finance",
                "apply_url": "https://example.com/accountant",
            }],
            [],
        )
        listing_repository = Mock()
        listing_repository.search.return_value = []
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            Mock(return_value=live_jobs),
            Mock(side_effect=lambda _profile, jobs: jobs),
            job_listing_repository=listing_repository,
        )

        service.search_for_user(42, keyword="Accountant")

        listing_repository.upsert_many.assert_called_once_with(list(live_jobs))

    def test_stored_search_failure_rolls_back_and_uses_live_providers(self):
        live_jobs = AggregatedJobs(
            [{
                "title": "Accountant",
                "company": "Example Finance",
                "apply_url": "https://example.com/accountant",
            }],
            [{
                "name": "Example provider",
                "status": "active",
                "count": 1,
            }],
        )
        listing_repository = Mock()
        listing_repository.search.side_effect = RuntimeError(
            "database unavailable"
        )
        aggregator = Mock(return_value=live_jobs)
        service = JobSearchService(
            self.repository,
            self.resume_repository,
            aggregator,
            Mock(side_effect=lambda _profile, jobs: jobs),
            job_listing_repository=listing_repository,
        )

        result = service.search_for_user(42, keyword="Accountant")

        listing_repository.rollback.assert_called_once()
        aggregator.assert_called_once()
        self.assertEqual(result["providers"], live_jobs.provider_status)


if __name__ == "__main__":
    unittest.main()
