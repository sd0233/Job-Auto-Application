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


def login_naukri(driver) -> bool:
    """Login to Naukri with your credentials."""
    try:
        logger.info("[Naukri] Logging in...")
        driver.get("https://www.naukri.com/nlogin/login")
        time.sleep(random.uniform(3, 5))

        wait = WebDriverWait(driver, 15)

        # Enter email using correct id
        email_field = wait.until(
            EC.presence_of_element_located((By.ID, "usernameField"))
        )
        email_field.clear()
        email_field.send_keys(os.getenv("NAUKRI_EMAIL"))
        time.sleep(random.uniform(1, 2))

        # Enter password using correct id
        password_field = driver.find_element(By.ID, "passwordField")
        password_field.clear()
        password_field.send_keys(os.getenv("NAUKRI_PASSWORD"))
        time.sleep(random.uniform(1, 2))

        # Click login button
        login_btn = driver.find_element(By.XPATH, "//button[@type='submit']")
        login_btn.click()
        time.sleep(random.uniform(4, 6))

        # Verify login success
        if "naukri.com" in driver.current_url and "login" not in driver.current_url:
            logger.info("[Naukri] Login successful")
            return True
        else:
            logger.error("[Naukri] Login failed — check credentials in .env")
            return False

    except Exception as e:
        logger.error(f"[Naukri] Login error: {e}")
        return False

def fetch_naukri_jobs() -> list:
    with open("config.yaml") as f:
        config = yaml.safe_load(f)

    all_jobs = []
    driver = get_driver()

    try:
        # Login first
        if not login_naukri(driver):
            logger.error("[Naukri] Cannot proceed without login")
            return all_jobs

        time.sleep(random.uniform(3, 5))

        # Scrape each role + location combo
        for role in config["job_roles"]:
            for location in config["locations"]:
                jobs = _scrape_naukri(driver, role, location, config)
                all_jobs.extend(jobs)
                time.sleep(random.uniform(5, 10))

    finally:
        driver.quit()

    logger.info(f"[Naukri] Total jobs fetched: {len(all_jobs)}")
    return all_jobs


def _scrape_naukri(driver, role: str, location: str, config: dict) -> list:
    jobs = []

    try:
        role_slug     = role.lower().replace(" ", "-")
        location_slug = location.lower().replace(" ", "-")
        exp_min       = config["experience"]["min"]
        exp_max       = config["experience"]["max"]

        url = (
            f"https://www.naukri.com/{role_slug}-jobs-in-{location_slug}"
            f"?experienceList={exp_min}to{exp_max}"
        )

        driver.get(url)
        time.sleep(random.uniform(4, 7))

        # Wait for cards
        wait = WebDriverWait(driver, 15)
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".srp-jobtuple-wrapper")
                )
            )
        except:
            logger.warning(
                f"[Naukri] No jobs found for '{role}' in {location}"
            )
            return jobs

        cards = driver.find_elements(By.CSS_SELECTOR, ".srp-jobtuple-wrapper")

        for card in cards:
            try:
                # Title + URL — first <a> tag in card
                try:
                    title_el = card.find_elements(By.TAG_NAME, "a")[0]
                    title    = title_el.text.strip()
                    link     = title_el.get_attribute("href")
                except:
                    title = "N/A"
                    link  = ""

                # Company — second <a> tag
                try:
                    company = card.find_elements(By.TAG_NAME, "a")[1].text.strip()
                except:
                    company = "N/A"

                # Experience
                try:
                    exp = card.find_element(
                        By.CSS_SELECTOR, "span.expwdth"
                    ).text.strip()
                except:
                    exp = ""

                # Location
                try:
                    loc_txt = card.find_element(
                        By.CSS_SELECTOR, "span.locWdth"
                    ).text.strip()
                except:
                    loc_txt = location

                # Posted date
                try:
                    posted = card.find_element(
                        By.CSS_SELECTOR, "span.job-post-day"
                    ).text.strip()
                except:
                    posted = ""

                # Job key from URL
                if link:
                    job_key = f"naukri_{link.split('/')[-1].split('?')[0]}"
                else:
                    job_key = f"naukri_{title}_{company}".replace(" ", "_").lower()

                if not title or title == "N/A":
                    continue

                jobs.append({
                    "title":       title,
                    "company":     company,
                    "location":    loc_txt,
                    "experience":  exp,
                    "posted":      posted,
                    "url":         link,
                    "platform":    "naukri",
                    "job_key":     job_key,
                    "description": ""
                })

            except Exception as e:
                logger.warning(f"[Naukri] Card parse error: {e}")
                continue

        logger.info(
            f"[Naukri] '{role}' in {location}: {len(jobs)} jobs found"
        )

    except Exception as e:
        logger.error(f"[Naukri] Failed for '{role}' in {location}: {e}")

    return jobs