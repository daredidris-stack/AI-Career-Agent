import json
import re

from ollama import chat

## Load profile
with open("profile.json", "r") as file:
    profile = json.load(file)

# Load jobs database
with open("jobs.json", "r") as file:
    jobs = json.load(file)

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


def analyze_job_match(job):
    prompt = f"""
You are an expert technical recruiter.

Analyze the match between this candidate and this job.

Candidate:
Name: {profile['name']}
Skills: {', '.join(profile['skills'])}
Experience: {', '.join(profile['experience'])}
Target Roles: {', '.join(profile['target_roles'])}

Job:
Title: {job['title']}
Company: {job['company']}
Location: {job['location']}
Required Skills: {', '.join(job['skills'])}

Return ONLY valid JSON.

Example:
{{
    "score": 85,
    "strengths": ["AWS", "Linux"],
    "missing_skills": ["Terraform"],
    "recommendation": "Learn Terraform and Kubernetes."
}}
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

    text = response.message.content

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
def analyze_resume():
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

def rank_jobs():
    results = []

    for job in jobs:
        analysis = analyze_job_match(job)

        results.append({
            "title": job["title"],
            "company": job["company"],
            "score": analysis["score"],
            "strengths": analysis["strengths"],
            "missing_skills": analysis["missing_skills"],
            "recommendation": analysis["recommendation"]
        })

    results.sort(key=lambda job: job["score"], reverse=True)

    return results

def skill_gap_analysis():
    all_skills = set()

    # Collect all skills required by all jobs
    for job in jobs:
        for skill in job["skills"]:
            all_skills.add(skill)

    # User's current skills
    user_skills = set(profile["skills"])

    # Find missing skills
    missing_skills = sorted(all_skills - user_skills)

    print("\n" + "=" * 50)
    print("📊 Skill Gap Analysis")
    print("=" * 50)

    print("\n✅ Your Current Skills")
    for skill in sorted(user_skills):
        print(f"✓ {skill}")

    print("\n📚 Missing Skills")
    for skill in missing_skills:
        print(f"• {skill}")

    prompt = f"""
You are an expert Cloud Career Coach.

Candidate Skills:
{', '.join(user_skills)}

Missing Skills:
{', '.join(missing_skills)}

Recommend the TOP 5 skills to learn first.
Explain why each one is important.
"""

    print("\n🤖 AI Recommendations...\n")

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    print(response.message.content)
    
def generate_learning_plan():

    prompt = f"""
    You are an expert Cloud Career Mentor.

    Candidate Profile

    Name: {profile['name']}

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

    print("\n🤖 Creating your personalized learning plan...\n")

    response = chat(
        model="qwen3:8b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    print(response.message.content)


while True:

    print("\n" + "=" * 50)
    print("🤖 AI Career Agent")
    print("=" * 50)

    print(f"Welcome back, {profile['name']}!\n")
    
    print("1. Career Advice")
    print("2. Learning Roadmap")
    print("3. Resume Advice")
    print("4. Find Matching Jobs")
    print("5. Career Ranking Report")
    print("6. Skill Gap Analysis")
    print("7. Personalized Learning Plan")
    print("8. Exit")

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

        report = analyze_resume()

        print("\nResume Analysis\n")

        print(f"Resume Score: {report['resume_score']}/100")
        print(f"ATS Score: {report['ats_score']}/100")

        print("\nStrengths")

        for item in report["strengths"]:
            print(f"• {item}")

        print("\nImprovements")

        for item in report["improvements"]:
            print(f"• {item}")

    elif choice == "4":
        print("\nAnalyzing job matches with AI...\n")

        for job in jobs:
            print("=" * 50)
            print(f"{job['title']} - {job['company']}")
            print("=" * 50)

            print(analyze_job_match(job))


    elif choice == "5":
        print("\nGenerating Career Ranking Report...\n")

        ranked_jobs = rank_jobs()

        print(f"\n🏆 Top Career Matches for {profile['name']}\n")

        for index, job in enumerate(ranked_jobs, start=1):

            print("=" * 50)
            print(f"#{index} {job['title']}")
            print(f"Company: {job['company']}")
            print(f"Match Score: {job['score']}%")
            print("=" * 50)

            print("\n✅ Strengths:")
            for skill in job["strengths"]:
                print(f"  • {skill}")

            print("\n📚 Skills to Improve:")
            for skill in job["missing_skills"]:
                print(f"  • {skill}")

            print("\n💡 Recommendation:")
            print(job["recommendation"])
            print()

    elif choice == "6":
        skill_gap_analysis()

    elif choice == "7":
        generate_learning_plan()

    elif choice == "8":
        print("\nGoodbye, Dare! 👋")
        break

else:
    print("\nInvalid option.")
