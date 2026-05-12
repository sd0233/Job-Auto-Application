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
                "content": f"Rate how well this job matches my profile on a scale of 1 to 10. Reply with ONLY a single number. No explanation. No text. Just the number.\n\nMY PROFILE:\n{MY_RESUME}\n\nJOB TITLE: {job_title}\nJOB DESCRIPTION: {job_description}"
            }],
            max_tokens=5
        )
        score = int(response.choices[0].message.content.strip())
        return max(1, min(10, score))
    except Exception as e:
        logger.warning(f"[Scorer] Failed to score '{job_title}': {e}")
        return 5
