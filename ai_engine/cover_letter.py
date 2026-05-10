from groq import Groq
import os
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

MY_RESUME = """
Name: Sahil Dhote
Role: Application Support Engineer at Vserv Infosystems (AMNS India)
Experience: 8 months supporting HRMS, Weighing Machine, Plant Production apps
Skills: Linux, SQL, Python, Shell Scripting, ServiceNow, REST APIs, Postman
Education: B.Tech CSE, Priyadarshini College Nagpur, 2024
Projects: Built HRMS Support Automation Toolkit automating 2-3 hrs of daily work
"""

def generate_cover_letter(job_title: str, company: str, job_description: str = "") -> str:
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
            max_tokens=300
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.warning(f"[CoverLetter] Failed for '{job_title}' at {company}: {e}")
        return ""