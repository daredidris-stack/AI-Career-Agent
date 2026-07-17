import json
import re

from ollama import chat


def _profile_value(profile, field_name, default=""):
    if profile is None:
        return default

    if isinstance(profile, dict):
        return profile.get(field_name, default) or default

    return getattr(profile, field_name, default) or default


def analyze_resume(resume_text, profile=None):

    technical_skills = _profile_value(
        profile,
        "technical_skills",
    )
    current_role = _profile_value(
        profile,
        "current_role",
        "Not provided",
    )
    target_role = _profile_value(
        profile,
        "target_role",
        "Not provided",
    )
    professional_summary = _profile_value(
        profile,
        "professional_summary",
        "Not provided",
    )

    prompt = f"""
You are an expert ATS resume reviewer.

Analyze this resume:

{resume_text}

Candidate profile context:

- Current role: {current_role}
- Target role: {target_role}
- Technical skills: {technical_skills or "Not provided"}
- Professional summary: {professional_summary}


Return ONLY valid JSON.

Format:

{{
    "resume_score": 0,
    "ats_score": 0,
    "strengths": [],
    "improvements": []
}}

Evaluate:

- ATS compatibility
- Technical skills
- Cloud engineering keywords
- AWS experience
- Linux
- Networking
- Python
- DevOps
- CI/CD
- Automation
- Infrastructure
- Resume structure
- Quantified achievements
- Career progression
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

        except:
            pass


    return {
        "resume_score": 0,
        "ats_score": 0,
        "strengths": [],
        "improvements": []
    }
