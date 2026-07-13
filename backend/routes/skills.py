from fastapi import APIRouter

from skill_gap import skill_gap_analysis


router = APIRouter()


@router.post("/skills/analyze")
def analyze_skills(request: dict):

    result = skill_gap_analysis(
        request["profile"],
        request["jobs"]
    )

    return result