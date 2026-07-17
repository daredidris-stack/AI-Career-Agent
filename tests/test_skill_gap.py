import unittest
from unittest.mock import patch

from skill_gap import skill_gap_analysis


JOBS = [
    {
        "title": "Cloud Engineer",
        "skills": ["AWS", "Docker", "Terraform"],
    },
    {
        "title": "DevOps Engineer",
        "skills": ["AWS", "CI/CD"],
    },
]


class SkillGapAnalysisTests(unittest.TestCase):
    @patch("skill_gap.ask_llm", return_value="Recommendation")
    def test_uses_normalized_database_profile_fields(
        self,
        mock_ask_llm,
    ):
        profile = {
            "technical_skills": ["AWS", "Python"],
            "years_experience": 4,
            "current_role": "Data Center Technician",
            "target_role": "Cloud Engineer",
            "professional_summary": "Operates production infrastructure.",
        }

        result = skill_gap_analysis(profile, JOBS)

        self.assertEqual(
            result,
            {
                "current_skills": ["AWS", "Python"],
                "missing_skills": [
                    "Docker",
                    "Terraform",
                    "CI/CD",
                ],
                "recommendation": "Recommendation",
            },
        )

        prompt = mock_ask_llm.call_args.args[0]
        self.assertIn("Years of experience: 4", prompt)
        self.assertIn("Target role: Cloud Engineer", prompt)

    @patch("skill_gap.ask_llm", return_value="Recommendation")
    def test_missing_profile_fields_use_safe_defaults(
        self,
        mock_ask_llm,
    ):
        result = skill_gap_analysis({}, JOBS)

        self.assertEqual(result["current_skills"], [])
        self.assertEqual(
            result["missing_skills"],
            ["Docker", "Terraform", "CI/CD", "AWS"],
        )
        self.assertIn(
            "Current role: Not provided",
            mock_ask_llm.call_args.args[0],
        )

    @patch("skill_gap.ask_llm", return_value="Recommendation")
    def test_accepts_comma_separated_skills_and_ignores_bad_jobs(
        self,
        _mock_ask_llm,
    ):
        profile = {
            "technical_skills": " aws, Python, AWS ",
        }
        jobs = [
            None,
            {"skills": None},
            {"skills": "AWS, Kubernetes"},
            {"title": "Missing skills"},
        ]

        result = skill_gap_analysis(profile, jobs)

        self.assertEqual(
            result["current_skills"],
            ["aws", "Python"],
        )
        self.assertEqual(
            result["missing_skills"],
            ["Kubernetes"],
        )


if __name__ == "__main__":
    unittest.main()
