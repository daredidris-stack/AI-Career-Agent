import json
import re

from ollama import chat

def analyze_resume(profile):
    prompt = f"""
You are an expert ATS resume reviewer.

Candidate:

Name: {profile['name']}
Education: {profile['education']}
Experience: {', '.join(profile['experience'])}
Skills: {', '.join(profile['skills'])}

Return ONLY JSON.

{{
    "resume_score": 82,
    "ats_score": 88,
    "strengths": [
        "Cloud Experience",
        "AWS"
    ],
    "improvements": [
        "Add Terraform",
        "Add Docker Projects",
        "Quantify achievements"
    ]
}}
"""

    response = chat(
        model="qwen3:8b",
        messages=[{"role": "user", "content": prompt}]
    )

    text = response.message.content

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except:
            pass

    return {
        "resume_score":0,
        "ats_score":0,
        "strengths":[],
        "improvements":[]
    }