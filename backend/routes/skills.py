from fastapi import APIRouter

router = APIRouter()


@router.post("/skills/analyze")
def analyze_skills(request: dict):
    return {
        "current_skills": ["AWS", "Linux", "Python"],
        "missing_skills": [
            "Docker",
            "Kubernetes",
            "Terraform"
        ],
        "recommendation": "Learn Docker first, then Kubernetes, then Terraform."
    }
