import json
from typing import Any

from sqlalchemy.orm import Session

from backend.models.resume_analysis import ResumeAnalysis


class ResumeAnalysisRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: int,
        filename: str,
        result: dict[str, Any],
    ) -> ResumeAnalysis:
        analysis = ResumeAnalysis(
            user_id=user_id,
            filename=filename,
            resume_score=result["resume_score"],
            ats_score=result["ats_score"],
            strengths=json.dumps(result["strengths"]),
            improvements=json.dumps(result["improvements"]),
            extracted_skills=json.dumps(result.get("skills") or []),
        )
        self.db.add(analysis)
        self.db.commit()
        self.db.refresh(analysis)
        return analysis

    def get_latest_skills_by_user_id(self, user_id: int) -> list[str]:
        analysis = self.get_latest_by_user_id(user_id)

        if not analysis:
            return []

        try:
            skills = json.loads(analysis.extracted_skills or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

        if not isinstance(skills, list):
            return []

        return [
            str(skill).strip()
            for skill in skills
            if str(skill).strip()
        ]

    def get_latest_by_user_id(
        self,
        user_id: int,
    ) -> ResumeAnalysis | None:
        return (
            self.db.query(ResumeAnalysis)
            .filter(ResumeAnalysis.user_id == user_id)
            .order_by(
                ResumeAnalysis.created_at.desc(),
                ResumeAnalysis.id.desc(),
            )
            .first()
        )
