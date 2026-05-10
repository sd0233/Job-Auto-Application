from groq import Groq
import os
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MY_RESUME = """
Name: Sahil Dhote
Role: Application Support Engineer at Vserv Infosystems (deployed at AMNS India)
Experience: 8 months
Skills: Linux, SQL, Python, Shell Scripting, ServiceNow, REST APIs, Postman, iDesk
Education: B.Tech CSE, Priyadarshini College Nagpur, 2024, CGPA 7.6
Target Roles: Application Support, Production Support, Cloud Support, Cloud Engineer
Certifications: AWS Cloud Practitioner (pursuing)
Projects: HRMS Support Automation Toolkit, Job Application Bot
"""

def score_job(job_title: str, job_description: str = "") -> int:
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{
                "role": "user",
                "content": f"""
Write a short modern cover letter for this job application.
Rules:
- Max 100 words
- No address headers, no date, no subject line
- Start directly with "Dear Hiring Manager,"
- Mention company name and role specifically
- Highlight 2-3 relevant skills
- End confidently

JOB TITLE: {job_title}
COMPANY: {company}
DESCRIPTION: {job_description}

MY PROFILE:
{MY_RESUME}
"""
            }],
            max_tokens=5
        )
        score = int(response.choices[0].message.content.strip())
        return max(1, min(10, score))

    except Exception as e:
        logger.warning(f"[Scorer] Failed to score '{job_title}': {e}")
        return 5