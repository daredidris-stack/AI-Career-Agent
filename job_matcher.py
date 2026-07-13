import json
import re

from services.ollama_service import ask_llm
from utils.prompts import JOB_MATCH_PROMPT



def analyze_job_match(profile, job):
    prompt = f"""
    {JOB_MATCH_PROMPT}
You are a senior technical recruiter with experience hiring Cloud Engineers, DevOps Engineers, and AI Engineers.

Your task is to evaluate how well a candidate matches a job posting.

=========================
CANDIDATE PROFILE
=========================

Name:
{profile['name']}

Skills:
{', '.join(profile['skills'])}

Experience:
{', '.join(profile['experience'])}

Target Roles:
{', '.join(profile['target_roles'])}

=========================
JOB
=========================

Title:
{job['title']}

Company:
{job['company']}

Location:
{job['location']}

Required Skills:
{', '.join(job['skills'])}

Job Description:
{job.get('description', '')}

=========================
INSTRUCTIONS
=========================

Carefully compare the candidate against the job.

Evaluate:

- Technical skills
- Cloud platforms
- Programming languages
- DevOps tools
- Certifications
- Experience
- Responsibilities

Scoring:

95-100 = Excellent match
85-94 = Strong match
70-84 = Good match
50-69 = Partial match
Below 50 = Weak match

Rules:

- Use ONLY the information provided.
- Do NOT assume the candidate has skills that are not listed.
- Missing skills must actually appear in the job.
- Different jobs should usually receive different scores.
- Recommendation must be one short sentence.

Return ONLY valid JSON in this format:

{{
    "score": <integer>,
    "strengths": [
        "<skill>",
        "<skill>"
    ],
    "missing_skills": [
        "<skill>",
        "<skill>"
    ],
    "recommendation": "<one sentence>"
}}
"""
    text = ask_llm(prompt)

    match = re.search(r"\{.*\}", text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    return {
        "score": 0,
        "strengths": [],
        "missing_skills": [],
        "recommendation": "Unable to analyze this job."
    }         