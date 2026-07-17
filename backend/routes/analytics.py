from fastapi import APIRouter


router = APIRouter()


@router.get("/analytics")
def get_analytics():

    return {
        "resume_score": 82,
        "ats_score": 88,
        "skills_completed": 7,

        "weekly_progress": [
            {
                "week": "Week 1",
                "score": 62
            },
            {
                "week": "Week 2",
                "score": 70
            },
            {
                "week": "Week 3",
                "score": 78
            },
            {
                "week": "Week 4",
                "score": 82
            }
        ]
    }