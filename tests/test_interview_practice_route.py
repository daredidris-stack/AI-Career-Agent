import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.models.schemas import InterviewPracticeCreate
from backend.routes.interview_practice import score_interview_answer


class InterviewPracticeRouteTests(unittest.TestCase):
    def test_score_passes_authenticated_owner_and_validated_answer(self):
        service = Mock()
        service.score_for_user.return_value = {"id": 3, "score": 72}
        request = InterviewPracticeCreate(
            role="Platform Engineer",
            interview_type="Technical interview",
            question="Describe a difficult production problem.",
            answer=(
                "I diagnosed a production issue, implemented the fix, and "
                "measured the result."
            ),
        )

        result = score_interview_answer(
            request,
            SimpleNamespace(id=9),
            service,
        )

        self.assertEqual(result["score"], 72)
        service.score_for_user.assert_called_once_with(
            9,
            request.role,
            request.interview_type,
            request.question,
            request.answer,
        )


if __name__ == "__main__":
    unittest.main()
