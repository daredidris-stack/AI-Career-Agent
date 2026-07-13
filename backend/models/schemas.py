from pydantic import BaseModel


class SkillAnalysisRequest(BaseModel):
    profile: dict
    jobs: list