import json
from ollama import chat

# Load profile
with open("profile.json", "r") as file:
    profile = json.load(file)
    # Load AI prompt
with open("prompts/career_prompt.txt", "r") as file:
    career_prompt = file.read()


def ask_ai(question):
    prompt = f"""
{career_prompt}

User Profile:

Name: {profile['name']}
Education: {profile['education']}
Experience: {', '.join(profile['experience'])}
Skills: {', '.join(profile['skills'])}
Target Roles: {', '.join(profile['target_roles'])}
Preferred Location: {profile['preferred_location']}

User Question:

{question}
"""

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.message.content


while True:

    print("\n" + "=" * 50)
    print("🤖 AI Career Agent")
    print("=" * 50)

    print(f"Welcome back, {profile['name']}!\n")

    print("1. Career Advice")
    print("2. Learning Roadmap")
    print("3. Resume Advice")
    print("4. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":
        question = input("\nWhat would you like to ask?\n> ")
        print("\nThinking...\n")
        print(ask_ai(question))

    elif choice == "2":
        print("\nThinking...\n")
        print(
            ask_ai(
                "Create a 6-month roadmap to help me reach my target roles."
            )
        )

    elif choice == "3":
        print("\nThinking...\n")
        print(
            ask_ai(
                "Review my profile and suggest improvements for my resume."
            )
        )

    elif choice == "4":
        print("\nGoodbye, Dare! 👋")
        break

    else:
        print("\nInvalid option.")
    