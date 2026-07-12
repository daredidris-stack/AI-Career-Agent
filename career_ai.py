from ollama import chat


def ask_ai(profile, career_prompt, question):

    prompt = f"""
{career_prompt}

User Profile

Name: {profile['name']}

Education:
{profile['education']}

Experience:
{', '.join(profile['experience'])}

Skills:
{', '.join(profile['skills'])}

Target Roles:
{', '.join(profile['target_roles'])}

Preferred Location:
{profile['preferred_location']}

User Question

{question}
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

    return response.message.content