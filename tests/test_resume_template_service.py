import unittest

from backend.services.resume_template_service import (
    DEFAULT_RESUME_TEMPLATE_ID,
    list_resume_templates,
    resolve_resume_template_id,
    resume_template_path,
    validate_template_request,
)


class ResumeTemplateServiceTests(unittest.TestCase):
    def test_lists_public_template_metadata(self):
        templates = list_resume_templates()

        self.assertEqual(len(templates), 3)
        self.assertEqual(templates[0]["id"], DEFAULT_RESUME_TEMPLATE_ID)
        self.assertTrue(templates[0]["is_default"])
        self.assertNotIn("filename", templates[0])

    def test_auto_uses_valid_agent_choice(self):
        self.assertEqual(
            resolve_resume_template_id("auto", "ats-modern"),
            "ats-modern",
        )

    def test_auto_falls_back_when_agent_choice_is_invalid(self):
        self.assertEqual(
            resolve_resume_template_id("auto", "invented-template"),
            DEFAULT_RESUME_TEMPLATE_ID,
        )

    def test_manual_choice_overrides_agent(self):
        self.assertEqual(
            resolve_resume_template_id("ats-classic", "ats-modern"),
            "ats-classic",
        )

    def test_rejects_unknown_manual_template(self):
        with self.assertRaises(ValueError):
            validate_template_request("unknown")

    def test_each_template_file_exists(self):
        for template in list_resume_templates():
            self.assertTrue(resume_template_path(template["id"]).exists())


if __name__ == "__main__":
    unittest.main()
