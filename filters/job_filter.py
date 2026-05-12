import yaml
import re
from utils.logger import get_logger

logger = get_logger()

def load_config():
    with open("config.yaml") as f:
        return yaml.safe_load(f)

def extract_min_experience(text: str):
    """
    Extract MINIMUM experience required from text.
    Examples:
      '1 to 3 years' -> 1
      '4-8 Yrs'      -> 4
      '0-5 years'    -> 0
      'Fresher'      -> 0
    Returns None if not found.
    """
    text = text.lower()

    # Fresher / entry level — always include
    fresher_keywords = [
        "fresher", "fresh graduate", "entry level",
        "entry-level", "0 year", "0-1 year", "0 to 1"
    ]
    if any(kw in text for kw in fresher_keywords):
        return 0

    patterns = [
        r'(\d+)\s*to\s*(\d+)\s*yr',
        r'(\d+)\s*-\s*(\d+)\s*yr',
        r'(\d+)\s*to\s*(\d+)\s*year',
        r'(\d+)\s*-\s*(\d+)\s*year',
        r'(\d+)\s*\+\s*yr',
        r'(\d+)\s*\+\s*year',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))  # return MINIMUM

    return None  # no experience info found


def filter_jobs(jobs: list, existing_keys: set) -> list:
    config     = load_config()
    exclude    = [kw.lower() for kw in config["filters"]["exclude_keywords"]]
    exp_max    = config["experience"]["max"]  # 5 from config.yaml
    filtered   = []
    skipped_exp = 0

    for job in jobs:
        # Skip already in DB
        if job.get("job_key") in existing_keys:
            continue

        # Skip excluded keywords
        title_lower = job.get("title", "").lower()
        desc_lower  = job.get("description", "").lower()
        combined    = title_lower + " " + desc_lower

        if any(kw in combined for kw in exclude):
            continue

        # Check experience from job's experience field + URL
        exp_text = job.get("experience", "")
        url_text = job.get("url", "")
        # Extract from URL e.g. '3-to-6-years' or '6-to-8-years'
        url_exp  = url_text.replace("-", " ").replace("to", "to")
        combined_exp = exp_text + " " + url_exp
        min_exp  = extract_min_experience(combined_exp)

        if min_exp is not None and min_exp > exp_max:
            skipped_exp += 1
            logger.info(
                f"[Filter] Skipped high exp ({exp_text}): {job.get('title')}"
            )
            continue

        filtered.append(job)

    if skipped_exp:
        logger.info(f"[Filter] Skipped {skipped_exp} jobs due to high experience")

    return filtered