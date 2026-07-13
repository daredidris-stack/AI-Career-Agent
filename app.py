import json
from pydoc import text
import re

from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from docx import Document

from resume_reader import read_pdf_resume
from docx_reader import read_docx_resume

from ollama import chat

from adzuna_api import search_jobs

from career_ai import ask_ai

from resume_analyzer import analyze_resume

from report_generator import (
    export_resume_report,
    export_resume_report_word,
)
from job_matcher import analyze_job_match

from resume_ai import generate_resume_content
from resume_writer import build_resume

from learning_plan import generate_learning_plan

from skill_gap import skill_gap_analysis

from cover_letter import generate_cover_letter
from cover_letter_writer import save_cover_letter

from interview_coach import generate_interview
from interview_writer import save_interview

## Load profile
with open("profile.json", "r") as file:
    profile = json.load(file)

# Load jobs database
with open("jobs.json", "r") as file:
    jobs = json.load(file)

# Load AI prompt
with open("prompts/career_prompt.txt", "r") as file:
    career_prompt = file.read()


def analyze_resume_pdf():

    filename = input("\nEnter resume filename: ")

    if filename.lower().endswith(".pdf"):
        resume_text = read_pdf_resume(filename)

    elif filename.lower().endswith(".docx"):
        resume_text = read_docx_resume(filename)

    else:
        print("\n❌ Unsupported file type.")
        return {
        "resume_score": 0,
        "ats_score": 0,
        "strengths": [],
        "improvements": []
    }

    prompt = f"""
    You are an expert ATS Resume Reviewer.

    Analyze this resume.

    Resume:

    {resume_text}

    Return ONLY valid JSON.

    {{
    "resume_score": 90,
    "ats_score": 88,
    "strengths": [],
    "improvements": []
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
        except:
            pass

    return {
        "resume_score": 0,
        "ats_score": 0,
        "strengths": [],
        "improvements": []
    }

def rank_jobs():
    results = []

    for job in jobs:
        analysis = analyze_job_match(profile, job)

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

    

while True:

    print("\n" + "=" * 50)
    print("🤖 AI Career Agent")
    print("=" * 50)

    print(f"Welcome back, {profile['name']}!\n")

    print("1. Career Advice")
    print("2. Learning Roadmap")
    print("3. Resume Advice (Profile)")
    print("4. Resume PDF Analysis")
    print("5. Find Matching Jobs")
    print("6. Career Ranking Report")
    print("7. Skill Gap Analysis")
    print("8. Personalized Learning Plan")
    print("9. Live AI Job Search")
    print("10. Tailor Resume")
    print("11. Generate Cover Letter")
    print("12. AI Interview Coach")
    print("13. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":

        question = input("\nWhat would you like to ask?\n> ")

        print("\nThinking...\n")

        print(
            ask_ai(
                profile,
                question
            )
        )

    elif choice == "2":

        print("\nThinking...\n")

        print(
            ask_ai(
                profile,
                "Create a 6-month roadmap to help me reach my target roles."
            )
        )

    elif choice == "3":

        report = analyze_resume(profile)

        print("\nResume Analysis\n")

        print(f"Resume Score: {report['resume_score']}/100")
        print(f"ATS Score: {report['ats_score']}/100")

        print("\nStrengths")
        for item in report["strengths"]:
            print(f"• {item}")

        print("\nImprovements")
        for item in report["improvements"]:
            print(f"• {item}")

        export_resume_report(report)
        export_resume_report_word(report)

    elif choice == "4":

        report = analyze_resume_pdf()

        print("\nResume Analysis\n")

        print(f"Resume Score: {report['resume_score']}/100")
        print(f"ATS Score: {report['ats_score']}/100")

        print("\nStrengths")
        for item in report["strengths"]:
            print(f"• {item}")

        print("\nImprovements")
        for item in report["improvements"]:
            print(f"• {item}")

        export_resume_report(report)
        export_resume_report_word(report)

    elif choice == "5":

        print("\n🤖 Analyzing job matches with AI...\n")

        ranked_jobs = []

        for job in jobs:

            report = analyze_job_match(profile, job)

            ranked_jobs.append({
                "job": job,
                "report": report
            })

        ranked_jobs.sort(
            key=lambda x: x["report"]["score"],
            reverse=True
        )

        print("=" * 60)
        print("🏆 BEST JOB MATCHES")
        print("=" * 60)

        for index, item in enumerate(ranked_jobs, start=1):

            job = item["job"]
            report = item["report"]

            print(f"\n#{index}")
            print("=" * 50)
            print(f"{job['title']} - {job['company']}")
            print("=" * 50)

            print(f"\nAI Match Score: {report['score']}%")

            if report["score"] >= 85:
                print("🟢 Excellent Match")
            elif report["score"] >= 70:
                print("🟡 Good Match")
            elif report["score"] >= 50:
                print("🟠 Needs Improvement")
            else:
                print("🔴 Weak Match")

            print("\n✅ Strengths")
            for skill in report["strengths"]:
                print(f"• {skill}")

            print("\n📚 Missing Skills")
            for skill in report["missing_skills"]:
                print(f"• {skill}")

            print("\n💡 Recommendation")
            print(report["recommendation"])

    elif choice == "6":

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
                print(f"• {skill}")

            print("\n📚 Skills to Improve:")
            for skill in job["missing_skills"]:
                print(f"• {skill}")

            print("\n💡 Recommendation:")
            print(job["recommendation"])
            print()

    elif choice == "7":

        report = skill_gap_analysis(profile, jobs)

        print("\n" + "=" * 50)
        print("📊 Skill Gap Analysis")
        print("=" * 50)

        print("\n✅ Your Current Skills")

        for skill in report["current_skills"]:
            print(f"✓ {skill}")

        print("\n📚 Missing Skills")

        for skill in report["missing_skills"]:
            print(f"• {skill}")

        print("\n🤖 AI Recommendations...\n")

        print(report["recommendation"])

    elif choice == "8":

        print("\n🤖 Creating your personalized learning plan...\n")

        print(
            generate_learning_plan(profile)
    )

    elif choice == "9":

        keyword = input("\nEnter job title: ")

        print("\nSearching live jobs...\n")

        jobs = search_jobs(keyword)

        if not jobs:
            print("No jobs found.")
            continue

        for job in jobs:

            print("=" * 60)
            print(f"Job Title : {job['title']}")
            print(f"Company   : {job['company']}")
            print(f"Location  : {job['location']}")

            print("\n🤖 AI is analyzing this job...\n")

            analysis = analyze_job_match(profile, job)

            print(f"AI Match Score: {analysis['score']}%")

            print("\n✅ Strengths")
            for skill in analysis["strengths"]:
                print(f"• {skill}")

            print("\n📚 Missing Skills")
            for skill in analysis["missing_skills"]:
                print(f"• {skill}")

            print("\n💡 Recommendation")
            print(analysis["recommendation"])

            print("\n🔗 Apply Here")
            print(job["redirect_url"])

            print()
            
    elif choice == "10":

        print("\nAvailable Jobs\n")

        for index, job in enumerate(jobs, start=1):
            print(f"{index}. {job['title']} - {job['company']}")

        selection = int(input("\nChoose a job number: ")) - 1

        if selection < 0 or selection >= len(jobs):
            print("\nInvalid selection.")
            continue

        selected_job = jobs[selection]

        print("\n🤖 Tailoring your resume...\n")



        ai_resume = generate_resume_content(
        profile,
        selected_job
    )

        filename = (
        "Tailored_Resume_"
        + selected_job["company"].replace(" ", "_")
        + ".docx"
    )

        build_resume(
            profile,
            ai_resume.get("summary", profile["summary"]),
            ai_resume.get("experience", {}),
            filename
    )

        print(f"\n✅ Tailored resume saved as {filename}")
        
    elif choice == "11":

        print("\nAvailable Jobs\n")

        for index, job in enumerate(jobs, start=1):
            print(f"{index}. {job['title']} - {job['company']}")

        selection = int(input("\nChoose a job number: ")) - 1

        if selection < 0 or selection >= len(jobs):
            print("Invalid selection.")
            continue

        selected_job = jobs[selection]

        print("\n🤖 Writing your cover letter...\n")

        letter = generate_cover_letter(
            profile,
            selected_job
        )

        filename = (
            "Cover_Letter_"
            + selected_job["company"].replace(" ", "_")
            + ".docx"
        )

        save_cover_letter(
            letter,
            filename
        )

        print(f"\n✅ Cover letter saved as {filename}")
        
    elif choice == "12":

        print("\nAvailable Jobs\n")

        for index, job in enumerate(jobs, start=1):
            print(f"{index}. {job['title']} - {job['company']}")

        selection = int(input("\nChoose a job number: ")) - 1

        if selection < 0 or selection >= len(jobs):
            print("\nInvalid selection.")
            continue

        selected_job = jobs[selection]

        print("\n🤖 Creating interview guide...\n")

        guide = generate_interview(
            profile,
            selected_job
        )

        filename = (
            "Interview_Guide_"
            + selected_job["company"].replace(" ", "_")
         + ".docx"
        )

        save_interview(
            guide,
            filename
        )

        print(f"\n✅ Interview guide saved as {filename}")

    elif choice == "13":

        print("\nGoodbye, Dare! 👋")
        break

    else:

        print("\nInvalid option.")