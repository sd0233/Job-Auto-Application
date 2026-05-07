from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import yaml
import time
import random
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
    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def is_captcha_page(driver):
    """Check if Indeed is showing a CAPTCHA or block page."""
    page = driver.page_source.lower()
    triggers = ["captcha", "robot", "unusual traffic", "verify you", "blocked"]
    return any(t in page for t in triggers)


def fetch_indeed_jobs() -> list:
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    all_jobs = []
    search_count = 0
    driver = get_driver()

    try:
        for role in config["job_roles"]:
            for location in config["locations"]:

                # Restart browser every 3 searches to avoid CAPTCHA
                if search_count > 0 and search_count % 3 == 0:
                    logger.info("[Indeed] Restarting browser to avoid CAPTCHA...")
                    driver.quit()
                    time.sleep(random.uniform(10, 20))  # cool down
                    driver = get_driver()

                jobs = _scrape_indeed(driver, role, location)
                all_jobs.extend(jobs)
                search_count += 1

                # Random delay between searches
                time.sleep(random.uniform(8, 15))

    finally:
        driver.quit()

    logger.info(f"[Indeed] Total jobs fetched: {len(all_jobs)}")
    return all_jobs


def _scrape_indeed(driver, role: str, location: str) -> list:
    jobs = []
    query = role.replace(" ", "+")
    loc   = location.replace(" ", "+")
    url   = (
        f"https://in.indeed.com/jobs?q={query}"
        f"&l={loc}&fromage=1&explvl=entry_level"
    )

    try:
        driver.get(url)
        time.sleep(random.uniform(6, 10))

        # Check for CAPTCHA
        if is_captcha_page(driver):
            logger.warning(
                f"[Indeed] CAPTCHA detected for '{role}' in {location} — skipping"
            )
            return jobs

        # Try to find job cards
        cards = driver.find_elements(By.CSS_SELECTOR, "div.job_seen_beacon")
        if not cards:
            cards = driver.find_elements(By.CSS_SELECTOR, "[data-jk]")

        for card in cards:
            try:
                # Title
                try:
                    title = card.find_element(
                        By.CSS_SELECTOR, "h2.jobTitle span"
                    ).text.strip()
                except:
                    title = card.find_element(By.CSS_SELECTOR, "h2").text.strip()

                # Company
                try:
                    company = card.find_element(
                        By.CSS_SELECTOR, "[data-testid='company-name']"
                    ).text.strip()
                except:
                    company = "N/A"

                # Location
                try:
                    loc_txt = card.find_element(
                        By.CSS_SELECTOR, "[data-testid='text-location']"
                    ).text.strip()
                except:
                    loc_txt = location

                # Job key + URL
                job_key = card.get_attribute("data-jk") or ""
                if job_key:
                    link = f"https://in.indeed.com/viewjob?jk={job_key}"
                else:
                    try:
                        link = card.find_element(
                            By.TAG_NAME, "a"
                        ).get_attribute("href")
                        job_key = link.split("jk=")[-1].split("&")[0]
                    except:
                        link    = url
                        job_key = f"{title}_{company}".replace(" ", "_").lower()

                if not title or title == "N/A":
                    continue

                jobs.append({
                    "title":       title,
                    "company":     company,
                    "location":    loc_txt,
                    "url":         link,
                    "platform":    "indeed",
                    "job_key":     f"indeed_{job_key}",
                    "description": ""
                })

            except Exception as e:
                logger.warning(f"[Indeed] Card parse error: {e}")
                continue

        logger.info(
            f"[Indeed] '{role}' in {location}: {len(jobs)} jobs found"
        )

    except Exception as e:
        logger.error(f"[Indeed] Failed for '{role}' in {location}: {e}")

    return jobs