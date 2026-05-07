import time
import random

def random_delay(min_sec=3, max_sec=8):
    """Random delay between actions to avoid bot detection."""
    delay = random.uniform(min_sec, max_sec)
    time.sleep(delay)
    return delay

def safe_find(driver, by, value):
    """Find element safely without crashing if not found."""
    try:
        return driver.find_element(by, value)
    except:
        return None

def safe_click(driver, by, value):
    """Click element safely."""
    element = safe_find(driver, by, value)
    if element:
        try:
            element.click()
            return True
        except:
            return False
    return False