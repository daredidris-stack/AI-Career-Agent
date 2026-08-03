from sqlalchemy.orm import Session

from backend.models.interview_practice import InterviewPracticeAttempt


class InterviewPracticeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, **values) -> InterviewPracticeAttempt:
        attempt = InterviewPracticeAttempt(**values)
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def list_for_user(
        self,
        user_id: int,
        limit: int = 20,
    ) -> list[InterviewPracticeAttempt]:
        return (
            self.db.query(InterviewPracticeAttempt)
            .filter(InterviewPracticeAttempt.user_id == user_id)
            .order_by(InterviewPracticeAttempt.created_at.desc())
            .limit(limit)
            .all()
        )
