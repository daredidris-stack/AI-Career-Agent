import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from backend.services.interview_practice_service import (
    InterviewPracticeService,
)


class InterviewPracticeServiceTests(unittest.TestCase):
    def test_specific_structured_answer_scores_above_vague_answer(self):
        strong = (
            "The situation was a production service with high latency. "
            "My task was to restore the customer experience. I diagnosed the "
            "database query, implemented an index, and tested the rollout. "
            "The result reduced latency by 42% in two hours."
        )
        vague = "We worked on a problem and it went well for the team."

        strong_result = InterviewPracticeService.score_answer(strong)
        vague_result = InterviewPracticeService.score_answer(vague)

        self.assertGreater(strong_result["score"], vague_result["score"])
        self.assertEqual(
            set(strong_result["dimensions"]),
            {"clarity", "structure", "evidence", "ownership"},
        )

    def test_score_is_persisted_with_authenticated_owner(self):
        repository = Mock()
        repository.create.return_value = SimpleNamespace(
            id=4,
            role="Platform Engineer",
            interview_type="Technical interview",
            question="Describe a problem.",
            answer="I diagnosed and resolved a difficult production problem.",
            score=60,
            rubric_json='{"score": 60}',
            created_at=None,
        )
        service = InterviewPracticeService(repository)

        result = service.score_for_user(
            7,
            " Platform Engineer ",
            " Technical interview ",
            " Describe a problem. ",
            " I diagnosed and resolved a difficult production problem. ",
        )

        values = repository.create.call_args.kwargs
        self.assertEqual(values["user_id"], 7)
        self.assertEqual(values["role"], "Platform Engineer")
        self.assertEqual(result["id"], 4)


if __name__ == "__main__":
    unittest.main()
