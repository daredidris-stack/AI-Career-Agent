import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from backend.services.job_match_service import (
    JobMatchError,
    JobMatchService,
    ProfileRequiredError,
)


class JobMatchServiceTests(unittest.TestCase):
    def setUp(self):
        self.profile = SimpleNamespace(
            current_role="Technician",
            target_role="Cloud Engineer",
            years_experience=4,
            technical_skills="AWS, Linux, Python",
            professional_summary="Infrastructure operations",
        )
        self.repository = Mock()
        self.repository.get_by_user_id.return_value = self.profile
        self.service = JobMatchService(self.repository)

    @patch("backend.services.job_match_service.chat")
    def test_matches_job_with_profile_context(self, mock_chat):
        mock_chat.return_value.message.content = """
        {
            "match_score": 82,
            "matching_skills": ["AWS", "Linux"],
            "missing_skills": ["Terraform"],
            "recommendation": "Build an IaC project."
        }
        """

        result = self.service.match_for_user(
            6,
            "Supported AWS and Linux infrastructure.",
            "Cloud Engineer role",
        )

        self.repository.get_by_user_id.assert_called_once_with(6)
        self.assertEqual(result["match_score"], 82)
        self.assertEqual(
            result["matching_skills"],
            ["AWS", "Linux"],
        )
        prompt = mock_chat.call_args.kwargs["messages"][0]["content"]
        self.assertIn("Target role: Cloud Engineer", prompt)

    def test_empty_resume_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "Resume cannot be empty",
        ):
            self.service.match_for_user(
                6,
                " ",
                "Cloud role",
            )

        self.repository.get_by_user_id.assert_not_called()

    def test_empty_job_description_is_rejected(self):
        with self.assertRaisesRegex(
            ValueError,
            "Job description cannot be empty",
        ):
            self.service.match_for_user(
                6,
                "Resume",
                " ",
            )

    def test_missing_profile_stops_matching(self):
        self.repository.get_by_user_id.return_value = None

        with self.assertRaises(ProfileRequiredError):
            self.service.match_for_user(
                6,
                "Resume",
                "Cloud role",
            )

    @patch("backend.services.job_match_service.chat")
    def test_ai_failure_returns_service_error(self, mock_chat):
        mock_chat.side_effect = RuntimeError("Ollama unavailable")

        with self.assertRaises(JobMatchError):
            self.service.match_for_user(
                6,
                "Resume",
                "Cloud role",
            )

    @patch("backend.services.job_match_service.chat")
    def test_invalid_ai_response_returns_service_error(
        self,
        mock_chat,
    ):
        mock_chat.return_value.message.content = "not json"

        with self.assertRaises(JobMatchError):
            self.service.match_for_user(
                6,
                "Resume",
                "Cloud role",
            )

    def test_score_is_clamped_to_valid_range(self):
        result = self.service._parse_response(
            """
            {
                "match_score": 140,
                "matching_skills": [],
                "missing_skills": [],
                "recommendation": ""
            }
            """
        )

        self.assertEqual(result["match_score"], 100)


if __name__ == "__main__":
    unittest.main()
