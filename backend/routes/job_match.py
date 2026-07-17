from fastapi import APIRouter
from pydantic import BaseModel

from ollama import chat
import json
import re


router = APIRouter()


class JobMatchRequest(BaseModel):
    resume: str
    job_description: str



@router.post("/jobs/match")
def match_job(request: JobMatchRequest):


    prompt = f"""

You are an expert technical recruiter.

Analyze this resume:

RESUME:
{request.resume}


Against this job description:

JOB DESCRIPTION:
{request.job_description}


Return ONLY JSON.

Use realistic recruiter scoring.

Consider:
- Direct experience
- Transferable skills
- Technical skills
- Infrastructure experience
- Career progression


Format:

{{
    "match_score": 0,
    "matching_skills": [],
    "missing_skills": [],
    "recommendation": ""
}}

"""


    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role":"user",
                "content":prompt
            }
        ]
    )


    text = response.message.content


    match = re.search(
        r"\{.*\}",
        text,
        re.DOTALL
    )


    if match:

        try:

            result = json.loads(match.group())


            # Improve score realism

            skills = [
                "AWS",
                "Linux",
                "Python",
                "Networking",
                "Troubleshooting"
            ]


            resume_lower = request.resume.lower()


            base_score = 0


            for skill in skills:

                if skill.lower() in resume_lower:

                    base_score += 10



            if result["match_score"] < base_score:

                result["match_score"] = base_score



            return result


        except:

            pass



    return {

        "match_score":0,

        "matching_skills":[],

        "missing_skills":[],

        "recommendation":"Unable to analyze"

    }