from services.ollama_service import ask_llm
from utils.prompts import RESUME_PROMPT
import json
import re


def generate_resume_content(profile, job):

    prompt = f"""
    {RESUME_PROMPT}
You are a professional resume writer.

The candidate information is factual.
Never invent information.

Candidate:

{json.dumps(profile, indent=2)}

Target Job:

{json.dumps(job, indent=2)}

Return ONLY valid JSON like this:

{{
    "summary":"Professional summary here.",

    "experience": {{
        "Data Center Technician IV":[
            "...",
            "...",
            "..."
        ],

        "Data Center Technician III":[
            "...",
            "...",
            "..."
        ],

        "Data Center Technician Intern":[
            "...",
            "...",
            "..."
        ]
    }}
}}
"""

    text = ask_llm(prompt)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        return json.loads(match.group())

    return {
        "summary": "",
        "experience": {}
    }