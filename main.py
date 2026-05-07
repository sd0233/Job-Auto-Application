import yaml
from database.db_setup   import init_db
from database.db_manager import save_job, get_applied_keys, get_stats
from scrapers.indeed_scraper import fetch_indeed_jobs
from filters.job_filter  import filter_jobs
from utils.logger        import get_logger

logger = get_logger()

def run_bot():
    logger.info("=" * 50)
    logger.info("Job Application Bot started")
    logger.info("=" * 50)

    # 1. Init DB
    init_db()

    # 2. Load config
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    # 3. Get already applied jobs
    existing_keys = get_applied_keys()
    logger.info(f"Already applied to {len(existing_keys)} jobs previously")

    # 4. Scrape
    all_jobs = []

    if config["platforms"].get("indeed"):
        logger.info("Scraping Indeed...")
        all_jobs += fetch_indeed_jobs()

    logger.info(f"Total raw jobs scraped: {len(all_jobs)}")

    # 5. Filter
    new_jobs = filter_jobs(all_jobs, existing_keys)
    logger.info(f"New jobs after filtering: {len(new_jobs)}")

    # 6. Save to DB (status = 'scraped' for now, applicator comes in Phase 2+)
    saved = 0
    for job in new_jobs:
        job["status"] = "scraped"
        if save_job(job):
            saved += 1

    # 7. Summary
    stats = get_stats()
    logger.info("=" * 50)
    logger.info(f"Run complete. Saved {saved} new jobs.")
    logger.info(f"DB Stats: {stats}")
    logger.info("=" * 50)

if __name__ == "__main__":
    run_bot()