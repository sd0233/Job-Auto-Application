import google.generativeai as genai
import os
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MY_RESUME = """
Name: Sahil Dhote
Role: Application Support Engineer at Vserv Infosystems (AMNS India)
Experience: 8 months supporting HRMS, Weighing Machine, Plant Production apps
Skills: Linux, SQL, Python, Shell Scripting, ServiceNow, REST APIs
Education: B.Tech CSE, Priyadarshini College Nagpur, 2024
"""

def generate_cover_letter(job_title: str, company: str, job_description: str = "") -> str:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
Write a short professional cover letter for this job.
- Max 120 words
- No fluff, no generic lines
- Mention the company name and role specifically
- Highlight relevant skills from my profile

JOB TITLE: {job_title}
COMPANY: {company}
DESCRIPTION: {job_description}

MY PROFILE:
{MY_RESUME}
"""
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.warning(f"[CoverLetter] Failed for '{job_title}' at {company}: {e}")
        return ""