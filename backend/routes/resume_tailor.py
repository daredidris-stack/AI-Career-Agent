import json
import os
import re
import shutil

from fastapi import APIRouter, File, Form, UploadFile
from ollama import chat

from docx_reader import read_docx_resume
from resume_reader import read_pdf_resume


router = APIRouter()


@router.post("/resume/tailor-upload")
async def tailor_resume_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    os.makedirs("uploads", exist_ok=True)
    file_path = f"uploads/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    if file.filename.lower().endswith(".pdf"):
        resume_text = read_pdf_resume(file_path)
    elif file.filename.lower().endswith(".docx"):
        resume_text = read_docx_resume(file_path)
    else:
        return {
            "error": "Only PDF and DOCX files are supported."
        }

    prompt = f"""
You are a professional resume writer.

Rewrite this resume so it matches the job description.

Resume:

{resume_text}

Job Description:

{job_description}

Return ONLY valid JSON.

{{
    "summary":"",
    "skills":[],
    "experience":[]
}}

Rules:

- Never invent experience.
- Improve ATS keywords.
- Rewrite professionally.
- Keep the candidate truthful.
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    match = re.search(
        r"\{.*\}",
        response.message.content,
        re.DOTALL,
    )

    if match:
        try:
            return json.loads(match.group())
        except (TypeError, ValueError):
            pass

    return {
        "summary": "",
        "skills": [],
        "experience": [],
    }
