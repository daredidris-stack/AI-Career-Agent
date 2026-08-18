import json
import re
from typing import Any

from backend.models.profile import Profile
from backend.repositories.interview_practice_repository import (
    InterviewPracticeRepository,
)
from backend.repositories.profile_repository import ProfileRepository


class InterviewPracticeService:
    def __init__(
        self,
        repository: InterviewPracticeRepository,
        profile_repository: ProfileRepository,
    ):
        self.repository = repository
        self.profile_repository = profile_repository

    def score_for_user(
        self,
        user_id: int,
        role: str,
        interview_type: str,
        question: str,
        answer: str,
    ) -> dict[str, Any]:
        cleaned_answer = answer.strip()
        profile = self.profile_repository.get_by_user_id(user_id)
        rubric = self.score_answer(cleaned_answer, profile)
        attempt = self.repository.create(
            user_id=user_id,
            role=role.strip(),
            interview_type=interview_type.strip(),
            question=question.strip(),
            answer=cleaned_answer,
            score=rubric["score"],
            rubric_json=json.dumps(rubric, sort_keys=True),
        )
        return self._response(attempt)

    def list_for_user(self, user_id: int) -> list[dict[str, Any]]:
        return [
            self._response(attempt)
            for attempt in self.repository.list_for_user(user_id)
        ]

    @staticmethod
    def score_answer(answer: str, profile: Profile | None = None) -> dict[str, Any]:
        words = re.findall(r"\b[\w'-]+\b", answer)
        word_count = len(words)
        normalized = answer.casefold()

        if 60 <= word_count <= 260:
            clarity = 25
            clarity_feedback = "The answer is a focused practice length."
        elif 35 <= word_count < 60 or 260 < word_count <= 360:
            clarity = 18
            clarity_feedback = "Tighten or expand the answer toward 60–260 words."
        else:
            clarity = 8
            clarity_feedback = "Use enough detail for a complete example without overexplaining."

        structure_groups = [
            ("situation", "context", "challenge", "when"),
            ("task", "goal", "responsibility", "needed to"),
            ("action", "implemented", "created", "led", "decided", "diagnosed"),
            ("result", "outcome", "impact", "improved", "reduced", "increased"),
        ]
        structure_hits = sum(
            any(cue in normalized for cue in group)
            for group in structure_groups
        )
        structure = structure_hits * 7
        if structure_hits == 4:
            structure += 2
        structure_feedback = (
            "The answer shows situation, responsibility, action, and result."
            if structure_hits == 4
            else "Make the situation, your responsibility, your action, and the result explicit."
        )

        has_number = bool(
            re.search(r"\b\d+(?:\.\d+)?%?\b", answer)
        )
        evidence_cues = sum(
            cue in normalized
            for cue in (
                "because",
                "by using",
                "measured",
                "customer",
                "latency",
                "revenue",
                "time",
                "cost",
            )
        )
        evidence = (15 if has_number else 5) + min(10, evidence_cues * 2)
        evidence_feedback = (
            "The answer includes a concrete number or measurable result."
            if has_number
            else "Add a truthful number, scale, time saved, quality change, or other measurable result."
        )

        ownership_hits = len(re.findall(
            r"\bi\s+(?:built|created|decided|designed|diagnosed|implemented|led|owned|proposed|resolved|tested|wrote)\b",
            normalized,
        ))
        ownership = 20 if ownership_hits >= 3 else 13 if ownership_hits else 5
        ownership_feedback = (
            "Your personal contribution is clear."
            if ownership_hits
            else "State what you personally decided and did, while still crediting the team."
        )

        # Personalize feedback based on profile
        if profile:
            target_role = profile.target_role
            years_experience = profile.years_experience
            if target_role:
                structure_feedback = f"For a {target_role} role, clearly outlining the situation, your responsibility, the actions you took, and the results is key. {structure_feedback}"
                evidence_feedback = f"In {target_role} positions, backing up your claims with concrete numbers or measurable outcomes strengthens your answer. {evidence_feedback}"
            # Optionally, we could adjust clarity based on years_experience, but we keep it simple for now.
        else:
            # Generic feedback when no profile
            structure_feedback = "In behavioral interviews, clearly outlining the situation, your responsibility, the actions you took, and the results is key. " + structure_feedback
            evidence_feedback = "In any role, backing up your claims with concrete numbers or measurable outcomes strengthens your answer. " + evidence_feedback

        score = min(100, clarity + structure + evidence + ownership)
        return {
            "score": score,
            "word_count": word_count,
            "dimensions": {
                "clarity": {
                    "score": clarity,
                    "max": 25,
                    "feedback": clarity_feedback,
                },
                "structure": {
                    "score": structure,
                    "max": 30,
                    "feedback": structure_feedback,
                },
                "evidence": {
                    "score": evidence,
                    "max": 25,
                    "feedback": evidence_feedback,
                },
                "ownership": {
                    "score": ownership,
                    "max": 20,
                    "feedback": ownership_feedback,
                },
            },
            "disclaimer": (
                "This is a structure and evidence practice score, not a "
                "judgment of technical correctness or hiring likelihood."
            ),
        }

    @classmethod
    def _response(cls, attempt) -> dict[str, Any]:
        try:
            rubric = json.loads(attempt.rubric_json)
        except (TypeError, json.JSONDecodeError):
            rubric = {}
        return {
            "id": attempt.id,
            "role": attempt.role,
            "interview_type": attempt.interview_type,
            "question": attempt.question,
            "answer": attempt.answer,
            "score": attempt.score,
            "rubric": rubric,
            "created_at": attempt.created_at,
        }
