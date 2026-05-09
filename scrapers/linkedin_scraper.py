from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import yaml
import time
import random
import os
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
logger = get_logger()


def get_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-images")  # faster load
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    options.page_load_strategy = "eager"  # don't wait for full page load
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(30)  # timeout after 30s max
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver

def login_linkedin(driver) -> bool:
    try:
        logger.info("[LinkedIn] Logging in...")
        driver.get("https://www.linkedin.com/login")
        time.sleep(10)

        driver.find_element(By.ID, "username").send_keys(os.getenv("LINKEDIN_EMAIL"))
        time.sleep(1)
        driver.find_element(By.ID, "password").send_keys(os.getenv("LINKEDIN_PASSWORD"))
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(8)

        current = driver.current_url
        logger.info(f"[LinkedIn] After login URL: {current}")

        if "feed" in current or "mynetwork" in current:
            logger.info("[LinkedIn] Login successful")
            return True
        elif "checkpoint" in current:
            logger.error("[LinkedIn] Security checkpoint hit")
            return False
        else:
            logger.info("[LinkedIn] Login successful")
            return True

    except Exception as e:
        logger.error(f"[LinkedIn] Login error: {e}")
        return False

def fetch_linkedin_jobs() -> list:
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    all_jobs = []
    driver = get_driver()

    try:
        if not login_linkedin(driver):
            logger.error("[LinkedIn] Cannot proceed without login")
            return all_jobs

        time.sleep(random.uniform(3, 5))

        for role in config["job_roles"]:
            for location in config["locations"]:
                jobs = _scrape_linkedin(driver, role, location, config)
                all_jobs.extend(jobs)
                # Longer delay for LinkedIn — very strict bot detection
                time.sleep(random.uniform(10, 18))

    finally:
        driver.quit()

    logger.info(f"[LinkedIn] Total jobs fetched: {len(all_jobs)}")
    return all_jobs

def _scrape_linkedin(driver, role: str, location: str, config: dict) -> list:
    jobs = []

    try:
        query = role.replace(" ", "%20")
        loc   = location.replace(" ", "%20")

        url = (
            f"https://www.linkedin.com/jobs/search/"
            f"?keywords={query}"
            f"&location={loc}"
            f"&f_TPR=r86400"
            f"&f_AL=true"
        )

        # Handle page load timeout gracefully
        try:
            driver.get(url)
        except Exception:
            pass  # eager strategy throws timeout but page is usable

        time.sleep(random.uniform(6, 9))

        # Check for auth wall
        if "authwall" in driver.current_url or "checkpoint" in driver.current_url:
            logger.warning(f"[LinkedIn] Auth wall for '{role}' in {location}")
            return jobs

        cards = driver.find_elements(By.CSS_SELECTOR, ".scaffold-layout__list li")

        for card in cards:
            try:
                text = card.text.strip()
                if len(text) < 20:
                    continue

                # Title + URL
                try:
                    links = card.find_elements(By.TAG_NAME, "a")
                    title_link = next(
                        (a for a in links if a.text.strip() and len(a.text.strip()) > 5),
                        None
                    )
                    title = title_link.text.strip() if title_link else "N/A"
                    link  = title_link.get_attribute("href").split("?")[0] if title_link else ""
                except:
                    title = "N/A"
                    link  = ""

                # Company + Location from spans
                spans = card.find_elements(By.TAG_NAME, "span")
                span_texts = [
                    s.text.strip() for s in spans
                    if s.text.strip() and len(s.text.strip()) > 1
                ]

                company = span_texts[0] if len(span_texts) > 0 else "N/A"
                loc_txt = span_texts[1] if len(span_texts) > 1 else location

                # Job key
                if link:
                    job_key = f"linkedin_{link.split('-')[-1]}"
                else:
                    job_key = f"linkedin_{title}_{company}".replace(" ", "_").lower()

                if not title or title == "N/A":
                    continue

                jobs.append({
                    "title":       title,
                    "company":     company,
                    "location":    loc_txt,
                    "url":         link,
                    "platform":    "linkedin",
                    "job_key":     job_key,
                    "description": ""
                })

            except Exception as e:
                logger.warning(f"[LinkedIn] Card parse error: {e}")
                continue

        logger.info(f"[LinkedIn] '{role}' in {location}: {len(jobs)} jobs found")

    except Exception as e:
        logger.error(f"[LinkedIn] Failed for '{role}' in {location}: {e}")

    return jobs