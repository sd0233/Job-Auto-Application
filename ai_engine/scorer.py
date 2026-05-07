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
Experience: 8 months
Skills: Linux, SQL, Python, Shell Scripting, ServiceNow, REST APIs, Postman, iDesk
Education: B.Tech CSE, Priyadarshini College Nagpur, 2024
Target Roles: Application Support, Production Support, Cloud Support, Cloud Engineer
"""

def score_job(job_title: str, job_description: str = "") -> int:
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = f"""
Rate how well this job matches my profile on a scale of 1 to 10.
Reply with ONLY a single number. No explanation, no text, just the number.

MY PROFILE:
{MY_RESUME}

JOB TITLE: {job_title}
JOB DESCRIPTION: {job_description}
"""
        response = model.generate_content(prompt)
        score = int(response.text.strip())
        return max(1, min(10, score))  # clamp between 1-10
    except Exception as e:
        logger.warning(f"[Scorer] Failed to score job '{job_title}': {e}")
        return 5  # safe default