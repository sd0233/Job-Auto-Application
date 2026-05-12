from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from utils.logger import get_logger

logger = get_logger()


def apply_naukri_job(driver, job_url: str, job_title: str, company: str) -> str:
    try:
        driver.get(job_url)
        time.sleep(random.uniform(4, 7))

        wait = WebDriverWait(driver, 15)

        # Check if already applied
        try:
            already = driver.find_element(
                By.XPATH, "//*[contains(text(),'Already Applied')]"
            )
            if already:
                logger.info(f"[Apply] Already applied: {job_title} @ {company}")
                return "skipped_already"
        except:
            pass

        # Find Apply button
        apply_btn = None
        try:
            apply_btn = driver.find_element(By.ID, "apply-button")
        except:
            pass

        if not apply_btn:
            try:
                apply_btn = driver.find_element(
                    By.CSS_SELECTOR, "button.apply-button"
                )
            except:
                pass

        if not apply_btn:
            logger.warning(f"[Apply] No apply button: {job_title} @ {company}")
            return "failed_no_button"

        # Check if external apply
        btn_text = apply_btn.text.strip().lower()
        if "company site" in btn_text or "external" in btn_text:
            logger.info(f"[Apply] External — skipping: {job_title} @ {company}")
            return "skipped_external"

        # Click Apply — use JS click to bypass overlays
        driver.execute_script("window.scrollTo(0, 400);")
        time.sleep(1)
        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", apply_btn)
        time.sleep(1)
        driver.execute_script("arguments[0].click();", apply_btn)
        time.sleep(random.uniform(3, 5))

        # Handle chatbot flow
        try:
            chatbot = driver.find_element(
                By.CSS_SELECTOR, ".chatbot_DrawerContent"
            )
            if chatbot:
                logger.info(f"[Apply] Chatbot flow: {job_title}")
                return _handle_chatbot_apply(driver)
        except:
            pass

        # Handle confirm popup
        try:
            confirm_btn = wait.until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//button[contains(text(),'Apply') and not(contains(text(),'Cancel'))]"
                ))
            )
            confirm_btn.click()
            time.sleep(random.uniform(2, 4))
        except:
            pass

        # Check success
        page_text = driver.page_source.lower()
        success_indicators = [
            "application submitted",
            "successfully applied",
            "already applied",
            "thank you for applying"
        ]
        if any(s in page_text for s in success_indicators):
            logger.info(f"[Apply] ✅ Applied: {job_title} @ {company}")
            return "applied"

        logger.info(f"[Apply] ✅ Applied (assumed): {job_title} @ {company}")
        return "applied"

    except Exception as e:
        logger.error(f"[Apply] Error for {job_title} @ {company}: {e}")
        return "failed"


def _handle_chatbot_apply(driver) -> str:
    try:
        max_steps = 10
        step = 0
        while step < max_steps:
            time.sleep(random.uniform(2, 3))
            btn_labels = [
                "//button[contains(text(),'Next')]",
                "//button[contains(text(),'Continue')]",
                "//button[contains(text(),'Submit')]",
                "//button[contains(text(),'Apply')]",
                "//button[contains(text(),'Confirm')]",
            ]
            clicked = False
            for label in btn_labels:
                try:
                    btn = driver.find_element(By.XPATH, label)
                    if btn.is_displayed() and btn.is_enabled():
                        btn.click()
                        clicked = True
                        step += 1
                        time.sleep(2)
                        break
                except:
                    continue

            page_text = driver.page_source.lower()
            if "successfully applied" in page_text or "application submitted" in page_text:
                return "applied"
            if not clicked:
                break
        return "applied"
    except Exception as e:
        logger.error(f"[Chatbot Apply] Error: {e}")
        return "failed"


def apply_all_naukri(driver, shortlisted_jobs: list, limit: int = 40) -> dict:
    results = {
        "applied": 0,
        "skipped_external": 0,
        "skipped_already": 0,
        "failed": 0
    }

    naukri_jobs = [j for j in shortlisted_jobs if j["platform"] == "naukri"]
    logger.info(f"[Apply] Starting — {len(naukri_jobs)} shortlisted Naukri jobs")

    for i, job in enumerate(naukri_jobs):
        if results["applied"] >= limit:
            logger.info(f"[Apply] Daily limit {limit} reached. Stopping.")
            break

        logger.info(
            f"[Apply] {i+1}/{len(naukri_jobs)} — "
            f"{job['title']} @ {job['company']}"
        )

        status = apply_naukri_job(
            driver,
            job["url"],
            job["title"],
            job["company"]
        )
        results[status] = results.get(status, 0) + 1

        from database.db_manager import update_status
        update_status(job["job_key"], status)

        time.sleep(random.uniform(8, 15))

    logger.info(f"[Apply] Naukri done: {results}")
    return results