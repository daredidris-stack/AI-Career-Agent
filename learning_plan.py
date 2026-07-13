from services.ollama_service import ask_llm
from utils.prompts import LEARNING_PROMPT


def generate_learning_plan(profile):

    prompt = f"""
{LEARNING_PROMPT}

Candidate Profile

Name:
{profile['name']}

Current Skills:
{', '.join(profile['skills'])}

Target Roles:
{', '.join(profile['target_roles'])}

Create a personalized 6-month learning roadmap.

For each month include:

• Main topics
• Mini projects
• Recommended certifications (if applicable)
• Expected outcome

Format the response nicely using Markdown.
"""

    return ask_llm(prompt)