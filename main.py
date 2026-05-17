import yaml
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from database.db_setup        import init_db
from database.db_manager      import save_job, get_applied_keys, get_stats, get_all_jobs
from scrapers.indeed_scraper  import fetch_indeed_jobs
from scrapers.naukri_scraper  import fetch_naukri_jobs, login_naukri
from scrapers.linkedin_scraper import fetch_linkedin_jobs
from filters.job_filter       import filter_jobs
from ai_engine.scorer         import score_job
from ai_engine.cover_letter   import generate_cover_letter
from applicators.naukri_apply import apply_all_naukri
from applicators.linkedin_apply import apply_all_linkedin
from utils.logger             import get_logger

logger = get_logger()


def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.page_load_strategy = "eager"
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def run_bot():
    logger.info("=" * 50)
    logger.info("Job Application Bot started")
    logger.info("=" * 50)

    init_db()

    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    existing_keys = get_applied_keys()
    logger.info(f"Already applied to {len(existing_keys)} jobs previously")

    all_jobs = []

    if config["platforms"].get("indeed"):
        logger.info("Scraping Indeed...")
        all_jobs += fetch_indeed_jobs()

    if config["platforms"].get("naukri"):
        logger.info("Scraping Naukri...")
        all_jobs += fetch_naukri_jobs()

    if config["platforms"].get("linkedin"):
        logger.info("Scraping LinkedIn...")
        all_jobs += fetch_linkedin_jobs()

    logger.info(f"Total raw jobs scraped: {len(all_jobs)}")

    new_jobs = filter_jobs(all_jobs, existing_keys)
    logger.info(f"New jobs after filtering: {len(new_jobs)}")

    # ── AI Scoring ────────────────────────────────
    skipped = 0
    saved   = 0
    min_score = config.get("min_ai_score", 6)

    for job in new_jobs:
        score = score_job(
            job.get("title", ""),
            job.get("description", "")
        )
        job["ai_score"] = score

        if score >= min_score:
            job["status"] = "shortlisted"
            logger.info(
                f"✅ [{score}/10] {job['title']} @ "
                f"{job.get('company', '?')} ({job['platform']})"
            )
        else:
            job["status"] = "skipped_low_score"
            skipped += 1
            logger.info(
                f"⬇️  [{score}/10] Skipped: {job['title']} @ "
                f"{job.get('company', '?')}"
            )

        if save_job(job):
            saved += 1

        time.sleep(random.uniform(0.5, 1.5))

    logger.info(f"Scoring done. Saved: {saved} | Skipped: {skipped}")

    # ── Auto Apply ────────────────────────────────
    # Fetch ALL shortlisted jobs from DB (current + previous runs)
    if config["platforms"].get("naukri"):
        all_db_jobs   = get_all_jobs()
        pending_apply = [
            j for j in all_db_jobs
            if j["status"] == "shortlisted"
            and j["platform"] == "naukri"
            and j.get("url")
        ]

        logger.info(f"Pending Naukri applications in DB: {len(pending_apply)}")

        if pending_apply:
            logger.info("Starting Naukri auto-apply...")
            driver = get_driver()
            try:
                if login_naukri(driver):
                    apply_all_naukri(
                        driver,
                        pending_apply,
                        limit=config.get("apply_limit_per_day", 40)
                    )
            finally:
                driver.quit()
    
    # ── LinkedIn Auto Apply ───────────────────────
    if config["platforms"].get("linkedin"):
        all_db_jobs      = get_all_jobs()
        linkedin_pending = [
            j for j in all_db_jobs
            if j["status"] == "shortlisted"
            and j["platform"] == "linkedin"
            and j.get("url")
        ]

        logger.info(f"Pending LinkedIn applications: {len(linkedin_pending)}")

        if linkedin_pending:
            logger.info("Starting LinkedIn auto-apply...")
            from scrapers.linkedin_scraper import login_linkedin
            driver = get_driver()
            try:
                if login_linkedin(driver):
                    apply_all_linkedin(
                        driver,
                        linkedin_pending,
                        limit=25  # LinkedIn max 25/day
                    )
            finally:
                driver.quit()
    # ── Summary ───────────────────────────────────
    stats = get_stats()
    logger.info("=" * 50)
    logger.info(f"Run complete. Saved {saved} new jobs.")
    logger.info(f"DB Stats: {stats}")
    logger.info("=" * 50)


if __name__ == "__main__":
    run_bot()