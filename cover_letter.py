from services.ollama_service import ask_llm
from utils.prompts import COVER_LETTER_PROMPT


def generate_cover_letter(profile, job):

    prompt = f"""
{COVER_LETTER_PROMPT}

Candidate

Name:
{profile['name']}

Education:
{profile['education']['degree']}

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

Location:
{job['location']}

Required Skills:
{', '.join(job['skills'])}

Write the cover letter.
"""

    return ask_llm(prompt)