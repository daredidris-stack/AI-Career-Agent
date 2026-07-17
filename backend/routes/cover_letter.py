from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ollama import chat


router = APIRouter()


class CoverLetterRequest(BaseModel):
    resume: str
    job_description: str



@router.post("/cover-letter")
def generate_cover_letter(request: CoverLetterRequest):

    if not request.resume.strip():
        raise HTTPException(
            status_code=400,
            detail="Resume cannot be empty"
        )


    if not request.job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description cannot be empty"
        )



    prompt = f"""
You are an expert technical recruiter and career coach.

Create a professional cover letter customized for this job.

Candidate Resume:

{request.resume}


Target Job Description:

{request.job_description}


Rules:

- Write approximately 300 words.
- Use a professional hiring-manager tone.
- Only mention skills and experience present in the resume.
- Do not create fake companies, projects, certifications, or achievements.
- Connect the candidate's experience to the job requirements.
- Highlight relevant technical skills.
- End with a confident professional closing.


Return ONLY the cover letter.
"""



    try:

        response = chat(
            model="qwen3:8b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )


        return {
            "cover_letter": response.message.content
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"AI generation failed: {str(error)}"
        )