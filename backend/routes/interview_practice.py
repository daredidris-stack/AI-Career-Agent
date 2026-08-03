from fastapi import APIRouter, Depends

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_interview_practice_service
from backend.models.schemas import InterviewPracticeCreate
from backend.models.user import User
from backend.services.interview_practice_service import InterviewPracticeService


router = APIRouter(prefix="/interview/practice", tags=["Interview Practice"])


@router.get("")
def list_interview_practice(
    current_user: User = Depends(get_current_user),
    service: InterviewPracticeService = Depends(
        get_interview_practice_service
    ),
):
    return service.list_for_user(current_user.id)


@router.post("", status_code=201)
def score_interview_answer(
    request: InterviewPracticeCreate,
    current_user: User = Depends(get_current_user),
    service: InterviewPracticeService = Depends(
        get_interview_practice_service
    ),
):
    return service.score_for_user(
        current_user.id,
        request.role,
        request.interview_type,
        request.question,
        request.answer,
    )
