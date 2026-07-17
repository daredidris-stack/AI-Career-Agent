from fastapi import APIRouter, Depends, HTTPException

from backend.dependencies.auth import get_current_user
from backend.dependencies.services import get_ai_usage_service, get_skill_gap_service
from backend.models.user import User
from backend.services.ai_usage_service import AIUsageService, reserve_ai_usage
from backend.services.skill_gap_service import (
    ProfileRequiredError,
    SkillGapError,
    SkillGapService,
)


router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
)


@router.post("/analyze")
def analyze_skills(
    current_user: User = Depends(get_current_user),
    service: SkillGapService = Depends(
        get_skill_gap_service
    ),
    usage: AIUsageService = Depends(get_ai_usage_service),
):
    reserve_ai_usage(usage, current_user.id, "skill_gap")
    try:
        return service.analyze_for_user(current_user.id)
    except ProfileRequiredError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        ) from error
    except SkillGapError as error:
        raise HTTPException(
            status_code=502,
            detail=str(error),
        ) from error
