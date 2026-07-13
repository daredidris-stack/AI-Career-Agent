from services.ollama_service import ask_llm


def skill_gap_analysis(profile, jobs):

    all_skills = set()

    for job in jobs:
        for skill in job["skills"]:
            all_skills.add(skill)

    user_skills = set(profile["skills"])

    missing_skills = sorted(all_skills - user_skills)

    prompt = f"""
You are an expert Cloud Career Coach.

Candidate Skills:
{', '.join(sorted(user_skills))}

Missing Skills:
{', '.join(missing_skills)}

Recommend the TOP 5 skills to learn first.

Explain why each one is important.
"""

    recommendation = ask_llm(prompt)

    return {
        "current_skills": sorted(user_skills),
        "missing_skills": missing_skills,
        "recommendation": recommendation
    }