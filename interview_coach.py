from services.ollama_service import ask_llm
from utils.prompts import INTERVIEW_PROMPT


def generate_interview(profile, job):

    prompt = f"""
{INTERVIEW_PROMPT}

Candidate

Name:
{profile['name']}

Skills:
{', '.join(profile['skills'])}

Experience:
"""

    for exp in profile["experience"]:
        prompt += f"""
- {exp['role']} at {exp['company']}
"""

    prompt += f"""

Job

Title:
{job['title']}

Company:
{job['company']}

Required Skills:
{', '.join(job['skills'])}

Generate the interview guide.
"""

    return ask_llm(prompt)