import unittest
from datetime import date
from unittest.mock import AsyncMock, Mock, patch

from fastapi import UploadFile

from backend.services.profile_autofill_service import (
    calculate_experience_years,
    clean_resume_text,
    extract_target_role_options,
    ProfileAutofillError,
    ProfileAutofillService,
    normalize_profile_autofill,
)


class ProfileAutofillServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.resume_service = Mock()
        self.resume_service.extract_text = AsyncMock(return_value="Resume text")
        self.service = ProfileAutofillService(self.resume_service)

    @patch(
        "backend.services.profile_autofill_service.extract_profile_from_resume"
    )
    async def test_extracts_and_normalizes_profile_fields(self, mock_extract):
        mock_extract.return_value = {
            "current_role": " Data Center Technician ",
            "years_experience": "7.0",
            "technical_skills": ["AWS", "Linux", "Python"],
            "linkedin": "linkedin.com/in/example-person",
            "github": "Not provided",
            "preferred_work_mode": "remote",
            "preferred_job_type": "unknown",
        }
        file = UploadFile(filename="resume.pdf", file=AsyncMock())

        result = await self.service.autofill_upload(file)

        self.resume_service.extract_text.assert_awaited_once_with(file)
        self.assertEqual(result["current_role"], "Data Center Technician")
        self.assertEqual(result["years_experience"], 7)
        self.assertEqual(result["technical_skills"], "AWS, Linux, Python")
        self.assertEqual(
            result["linkedin"],
            "https://linkedin.com/in/example-person",
        )
        self.assertIsNone(result["github"])
        self.assertEqual(result["preferred_work_mode"], "Remote")
        self.assertIsNone(result["preferred_job_type"])

    @patch(
        "backend.services.profile_autofill_service.extract_profile_from_resume",
        side_effect=RuntimeError("AI unavailable"),
    )
    async def test_ai_failure_is_reported(self, _mock_extract):
        file = UploadFile(filename="resume.pdf", file=AsyncMock())

        with self.assertRaises(ProfileAutofillError):
            await self.service.autofill_upload(file)

    def test_invalid_result_is_rejected(self):
        with self.assertRaises(ProfileAutofillError):
            normalize_profile_autofill(["not", "a", "profile"])

    def test_invalid_years_are_ignored(self):
        result = normalize_profile_autofill({"years_experience": "many"})

        self.assertIsNone(result["years_experience"])

    def test_null_list_items_are_ignored(self):
        result = normalize_profile_autofill({
            "technical_skills": ["AWS", None, "Linux"],
        })

        self.assertEqual(result["technical_skills"], "AWS, Linux")

    def test_invalid_urls_are_ignored(self):
        result = normalize_profile_autofill({
            "linkedin": "not a valid address",
            "portfolio": "portfolio.example.com/work",
        })

        self.assertIsNone(result["linkedin"])
        self.assertEqual(
            result["portfolio"],
            "https://portfolio.example.com/work",
        )

    def test_placeholder_phone_is_ignored(self):
        result = normalize_profile_autofill({
            "phone": "+1 (555) 123-4567",
        })

        self.assertIsNone(result["phone"])
        self.assertTrue(result["warnings"])

    def test_calculates_experience_from_employment_dates_only(self):
        resume_text = """
Education
University, 2018 - 2022
Professional Experience
AWS Data Center Technician
Jan 2022 - Present
Technical Skills
AWS, Linux
"""

        result = calculate_experience_years(
            resume_text,
            today=date(2026, 7, 21),
        )

        self.assertEqual(result, 4)

    def test_extracts_explicit_target_role_options(self):
        resume_text = """
Target Roles
AI Infrastructure Engineer, Cloud Engineer, DevOps Engineer
Projects (Optional)
Note: Add projects here.
"""

        self.assertEqual(
            extract_target_role_options(resume_text),
            [
                "AI Infrastructure Engineer",
                "Cloud Engineer",
                "DevOps Engineer",
            ],
        )

    def test_source_grounding_overrides_bad_ai_values(self):
        resume_text = """
Professional Experience
AWS Data Center Technician
Jan 2022 - Present
Technical Skills
AWS
Target Roles
Cloud Engineer, DevOps Engineer
"""

        result = normalize_profile_autofill(
            {
                "phone": "+1 (555) 123-4567",
                "target_role": "Invented role",
                "years_experience": 2,
            },
            resume_text=resume_text,
        )

        self.assertIsNone(result["phone"])
        self.assertEqual(result["target_role"], "Cloud Engineer")
        self.assertEqual(result["years_experience"], 4)
        self.assertEqual(
            result["target_role_options"],
            ["Cloud Engineer", "DevOps Engineer"],
        )

    def test_removes_markdown_and_template_notes_before_ai(self):
        resume_text = """
```markdown
**Technical Skills**
AWS, Linux
Projects (Optional)
*Note: Include relevant projects if applicable.*
```
"""

        cleaned = clean_resume_text(resume_text)

        self.assertNotIn("```", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("Include relevant projects", cleaned)


if __name__ == "__main__":
    unittest.main()
