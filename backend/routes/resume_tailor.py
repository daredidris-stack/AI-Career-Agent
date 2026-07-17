from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os
import json
import re

from ollama import chat
from resume_reader import read_pdf_resume
from docx_reader import read_docx_resume

router = APIRouter()


@router.post("/resume/tailor-upload")
async def tailor_resume_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...)
):

    # Create uploads folder
    os.makedirs("uploads", exist_ok=True)

    file_path = f"uploads/{file.filename}"

    # Save uploaded file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Read resume text
    if file.filename.lower().endswith(".pdf"):
        resume_text = read_pdf_resume(file_path)

    elif file.filename.lower().endswith(".docx"):
        resume_text = read_docx_resume(file_path)

    else:
        return {
            "error": "Only PDF and DOCX files are supported."
        }

    # AI Prompt
    prompt = f"""
You are an expert ATS resume writer.

Your job is to improve wording only.

Resume:

{resume_text}

Job Description:

{job_description}

IMPORTANT RULES

1. NEVER invent work experience.
2. NEVER invent years of experience.
3. NEVER invent projects.
4. NEVER invent certifications.
5. NEVER invent technologies the candidate has not used.
6. ONLY rewrite existing experience to sound more professional.
7. If a required skill is missing, DO NOT add it to the resume.
8. Instead, mention missing skills separately.

Return ONLY valid JSON.

{{
    "summary":"",
    "skills":[],
    "experience":[],
    "missing_skills":[]
}}
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
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
            return json.loads(match.group())
        except Exception:
            pass

    return {
        "summary": "",
        "skills": [],
        "experience": []
    }









from fastapi import APIRouter, UploadFile, File, Form
import shutil
import os
import json
import re

from ollama import chat

from resume_reader import read_pdf_resume
from docx_reader import read_docx_resume

router = APIRouter()


@router.post("/resume/tailor-upload")
async def tailor_resume_upload(
    file: UploadFile = File(...),
    job_description: str = Form(...)
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
                "content": prompt
            }
        ]
    )

    text = response.message.content

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    return {
        "summary": "",
        "skills": [],
        "experience": []
    }
