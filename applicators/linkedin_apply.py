from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from utils.logger import get_logger

logger = get_logger()


def apply_linkedin_job(driver, job_url: str, job_title: str, company: str) -> str:
    try:
        driver.get(job_url)
        time.sleep(random.uniform(4, 7))

        wait = WebDriverWait(driver, 10)

        # Check if already applied
        try:
            already = driver.find_element(
                By.XPATH, "//*[contains(text(),'Applied')]"
            )
            if already:
                logger.info(f"[LinkedIn Apply] Already applied: {job_title} @ {company}")
                return "skipped_already"
        except:
            pass

        # Find Easy Apply button
        easy_apply_btn = None
        try:
            easy_apply_btn = driver.find_element(
                By.CSS_SELECTOR, "button.jobs-apply-button"
            )
        except:
            pass

        if not easy_apply_btn:
            try:
                easy_apply_btn = driver.find_element(
                    By.XPATH,
                    "//button[contains(@aria-label,'Easy Apply')]"
                )
            except:
                pass

        if not easy_apply_btn:
            try:
                easy_apply_btn = driver.find_element(
                    By.XPATH,
                    "//button[contains(text(),'Easy Apply')]"
                )
            except:
                pass

        if not easy_apply_btn:
            logger.info(f"[LinkedIn Apply] No Easy Apply button: {job_title} @ {company}")
            return "skipped_external"

        # Click Easy Apply
        driver.execute_script("arguments[0].click();", easy_apply_btn)
        time.sleep(random.uniform(3, 5))

        # Handle multi-step modal
        max_steps = 10
        step = 0

        while step < max_steps:
            time.sleep(random.uniform(2, 3))

            # Check for error messages
            try:
                error = driver.find_element(
                    By.CSS_SELECTOR, ".artdeco-inline-feedback--error"
                )
                if error.is_displayed():
                    logger.warning(f"[LinkedIn Apply] Form error: {error.text}")
                    return "failed_form_error"
            except:
                pass

            # Try Next button
            try:
                next_btn = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='Continue to next step']"
                )
                if next_btn.is_displayed() and next_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", next_btn)
                    step += 1
                    time.sleep(2)
                    continue
            except:
                pass

            # Try Review button
            try:
                review_btn = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='Review your application']"
                )
                if review_btn.is_displayed() and review_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", review_btn)
                    step += 1
                    time.sleep(2)
                    continue
            except:
                pass

            # Try Submit button
            try:
                submit_btn = driver.find_element(
                    By.CSS_SELECTOR,
                    "button[aria-label='Submit application']"
                )
                if submit_btn.is_displayed() and submit_btn.is_enabled():
                    driver.execute_script("arguments[0].click();", submit_btn)
                    time.sleep(3)
                    logger.info(f"[LinkedIn Apply] ✅ Applied: {job_title} @ {company}")
                    return "applied"
            except:
                pass

            # Check success page
            page_text = driver.page_source.lower()
            if "application submitted" in page_text or "applied" in page_text:
                logger.info(f"[LinkedIn Apply] ✅ Applied: {job_title} @ {company}")
                return "applied"

            # Dismiss modal if stuck
            try:
                dismiss = driver.find_element(
                    By.CSS_SELECTOR, "button[aria-label='Dismiss']"
                )
                dismiss.click()
                time.sleep(2)
            except:
                pass

            break

        return "failed"

    except Exception as e:
        logger.error(f"[LinkedIn Apply] Error for {job_title} @ {company}: {e}")
        return "failed"


def apply_all_linkedin(driver, shortlisted_jobs: list, limit: int = 25) -> dict:
    results = {
        "applied": 0,
        "skipped_external": 0,
        "skipped_already": 0,
        "failed": 0,
        "failed_form_error": 0
    }

    linkedin_jobs = [
        j for j in shortlisted_jobs
        if j["platform"] == "linkedin" and j.get("url")
    ]

    logger.info(
        f"[LinkedIn Apply] Starting — {len(linkedin_jobs)} shortlisted jobs"
    )

    for i, job in enumerate(linkedin_jobs):
        # LinkedIn limit is lower — 25/day max
        if results["applied"] >= limit:
            logger.info(f"[LinkedIn Apply] Daily limit {limit} reached. Stopping.")
            break

        logger.info(
            f"[LinkedIn Apply] {i+1}/{len(linkedin_jobs)} — "
            f"{job['title']} @ {job['company']}"
        )

        status = apply_linkedin_job(
            driver,
            job["url"],
            job["title"],
            job["company"]
        )
        results[status] = results.get(status, 0) + 1

        from database.db_manager import update_status
        update_status(job["job_key"], status)

        # Longer delay for LinkedIn
        time.sleep(random.uniform(10, 18))

    logger.info(f"[LinkedIn Apply] Done: {results}")
    return results
