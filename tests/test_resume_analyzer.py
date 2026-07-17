import unittest
from types import SimpleNamespace
from unittest.mock import patch

from resume_analyzer import analyze_resume


class ResumeAnalyzerTests(unittest.TestCase):
    @patch("resume_analyzer.chat")
    def test_rejects_response_without_json(self, mock_chat):
        mock_chat.return_value = SimpleNamespace(
            message=SimpleNamespace(content="No structured result")
        )

        with self.assertRaisesRegex(ValueError, "did not return JSON"):
            analyze_resume("Resume text")

    @patch("resume_analyzer.chat")
    def test_rejects_malformed_json(self, mock_chat):
        mock_chat.return_value = SimpleNamespace(
            message=SimpleNamespace(content='{ "resume_score": }')
        )

        with self.assertRaisesRegex(ValueError, "malformed JSON"):
            analyze_resume("Resume text")


if __name__ == "__main__":
    unittest.main()
