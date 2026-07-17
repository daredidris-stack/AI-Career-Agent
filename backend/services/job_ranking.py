import json
import re

from ollama import chat
from services.ollama_service import reliable_chat


def _profile_value(profile, field_name, default=""):
    if isinstance(profile, dict):
        return profile.get(field_name, default) or default

    return getattr(profile, field_name, default) or default


def rank_jobs(profile, jobs):

    ranked_jobs = []

    technical_skills = _profile_value(
        profile,
        "technical_skills",
    )
    years_experience = _profile_value(
        profile,
        "years_experience",
        0,
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


    for job in jobs:

        prompt = f"""
You are a senior technical recruiter.

Analyze this candidate against this job.

Candidate:

- Current role: {current_role}
- Target role: {target_role}
- Years of experience: {years_experience}
- Technical skills: {technical_skills or "Not provided"}
- Professional summary: {professional_summary}


Job:

Title:
{job.get('title')}

Company:
{job.get('company')}

Description:
{job.get('description')}


Return ONLY JSON:

{{
"match_score":0,
"strengths":[],
"missing_skills":[],
"recommendation":""
}}

Consider:

- Direct experience
- Transferable skills
- AWS experience
- Linux
- Networking
- Python
- Cloud engineering progression

"""


        try:
            response = reliable_chat(
                prompt,
                chat_callable=chat,
                response_format="json",
            )
        except Exception:
            job["analysis"] = _unavailable_analysis()
            ranked_jobs.append(job)
            continue


        text = response.message.content


        match = re.search(
            r"\{.*\}",
            text,
            re.DOTALL
        )


        if match:

            try:

                analysis = json.loads(
                    match.group()
                )

                job["analysis"] = analysis

                ranked_jobs.append(job)


            except (TypeError, ValueError):
                job["analysis"] = _unavailable_analysis()
                ranked_jobs.append(job)

        else:
            job["analysis"] = _unavailable_analysis()
            ranked_jobs.append(job)



    ranked_jobs.sort(
        key=lambda x:
        x.get("analysis", {}).get("match_score") or 0,
        reverse=True
    )


    return ranked_jobs


def _unavailable_analysis():
    return {
        "match_score": None,
        "strengths": [],
        "missing_skills": [],
        "recommendation": (
            "AI ranking was unavailable for this listing."
        ),
    }
