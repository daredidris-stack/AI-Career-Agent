import unittest
from unittest.mock import Mock, patch

from backend.services.ai_usage_service import (
    AIUsageLimitError,
    AIUsageService,
)


class AIUsageServiceTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = AIUsageService(self.repository)

    def test_reserve_records_feature_when_below_limits(self):
        self.repository.count_since.side_effect = [2, 5]

        self.service.reserve(7, "cover_letter")

        self.repository.record.assert_called_once_with(7, "cover_letter")

    @patch("backend.services.ai_usage_service.AI_REQUESTS_PER_HOUR", 3)
    def test_hourly_limit_rejects_without_recording(self):
        self.repository.count_since.return_value = 3

        with self.assertRaisesRegex(AIUsageLimitError, "Hourly"):
            self.service.reserve(7, "job_match")

        self.repository.record.assert_not_called()

    @patch("backend.services.ai_usage_service.AI_REQUESTS_PER_DAY", 10)
    @patch("backend.services.ai_usage_service.AI_REQUESTS_PER_HOUR", 5)
    def test_daily_limit_rejects_without_recording(self):
        self.repository.count_since.side_effect = [1, 10]

        with self.assertRaisesRegex(AIUsageLimitError, "Daily"):
            self.service.reserve(7, "resume_analysis")

        self.repository.record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
