import unittest
from unittest.mock import Mock, patch

from backend.services.job_ranking import rank_jobs


class JobRankingTests(unittest.TestCase):
    @patch("backend.services.job_ranking.chat")
    def test_keeps_job_when_ai_response_is_malformed(self, mock_chat):
        mock_chat.return_value = Mock(
            message=Mock(content="No JSON returned")
        )
        job = {"title": "Platform Engineer"}

        result = rank_jobs({}, [job])

        self.assertEqual(len(result), 1)
        self.assertIsNone(result[0]["analysis"]["match_score"])

    @patch("backend.services.job_ranking.chat")
    def test_keeps_job_when_ai_provider_fails(self, mock_chat):
        mock_chat.side_effect = RuntimeError("Ollama unavailable")

        result = rank_jobs({}, [{"title": "Platform Engineer"}])

        self.assertEqual(len(result), 1)
        self.assertIn("unavailable", result[0]["analysis"]["recommendation"])


if __name__ == "__main__":
    unittest.main()
