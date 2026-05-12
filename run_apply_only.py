from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from database.db_setup import init_db
from database.db_manager import get_all_jobs
from scrapers.naukri_scraper import login_naukri
from applicators.naukri_apply import apply_all_naukri
from utils.logger import get_logger

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

init_db()
all_jobs = get_all_jobs()
pending  = [
    j for j in all_jobs
    if j["status"] == "shortlisted"
    and j["platform"] == "naukri"
    and j.get("url")
]

logger.info(f"Shortlisted jobs in DB: {len(pending)}")

if not pending:
    logger.info("No shortlisted jobs found. Run main.py with naukri enabled first.")
else:
    driver = get_driver()
    try:
        if login_naukri(driver):
            apply_all_naukri(driver, pending, limit=40)
    finally:
        driver.quit()
