from services.ollama_service import ask_llm
from utils.prompts import CAREER_PROMPT


def ask_ai(profile, question):

    prompt = f"""
{CAREER_PROMPT}

User Profile

Name: {profile['name']}

Education:
{profile['education']}

Experience:

{chr(10).join(
    f"- {job['role']} at {job['company']} ({job['start']} - {job['end']})"
    for job in profile["experience"]
)}

Skills:
{', '.join(profile['skills'])}

Target Roles:
{', '.join(profile['target_roles'])}

Preferred Location:
{profile['preferred_location']}

User Question

{question}
"""

    return ask_llm(prompt)