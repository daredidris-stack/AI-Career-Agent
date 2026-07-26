import unittest

from resume_text_cleaner import clean_resume_text


class ResumeTextCleanerTests(unittest.TestCase):
    def test_removes_literal_markdown_and_generator_notes(self):
        raw_text = """
```markdown
**Email:** person@example.com
--
## Technical Skills
**Cloud:** AWS, Linux
Projects (Optional)
*Note: Include relevant projects if applicable.*
```
**Note:** This resume emphasizes AWS and ATS-friendly keywords.
"""

        cleaned = clean_resume_text(raw_text)

        self.assertIn("Email: person@example.com", cleaned)
        self.assertIn("Technical Skills", cleaned)
        self.assertIn("Cloud: AWS, Linux", cleaned)
        self.assertNotIn("```", cleaned)
        self.assertNotIn("**", cleaned)
        self.assertNotIn("--", cleaned)
        self.assertNotIn("Projects (Optional)", cleaned)
        self.assertNotIn("Include relevant projects", cleaned)
        self.assertNotIn("This resume emphasizes", cleaned)

    def test_preserves_ordinary_hyphens_and_asterisks_inside_words(self):
        cleaned = clean_resume_text(
            "Cross-functional teamwork\nC* developer\nCI/CD"
        )

        self.assertEqual(
            cleaned,
            "Cross-functional teamwork\nC* developer\nCI/CD",
        )


if __name__ == "__main__":
    unittest.main()
