from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import os
from dotenv import load_dotenv

load_dotenv()

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

# Login
driver.get("https://www.linkedin.com/login")
time.sleep(5)

driver.execute_script(f"""
    document.getElementById('username').value = '{os.getenv("LINKEDIN_EMAIL")}';
    document.getElementById('password').value = '{os.getenv("LINKEDIN_PASSWORD")}';
""")
time.sleep(2)
driver.execute_script("document.querySelector(\"button[type='submit']\").click();")
time.sleep(7)

# Go to jobs search
url = (
    "https://www.linkedin.com/jobs/search/"
    "?keywords=Application%20Support"
    "&location=Pune"
    "&f_TPR=r86400"
    "&f_AL=true"
)
driver.get(url)
time.sleep(8)

print(f"Page title: {driver.title}")
print(f"Current URL: {driver.current_url}")

# Test selectors
selectors = [
    ".jobs-search__results-list li",
    ".scaffold-layout__list li",
    ".jobs-search-results__list li",
    ".job-card-container",
    ".jobs-search-results-list li",
    "ul.jobs-search__results-list li",
    ".job-card-list__entity-lockup",
    "div.job-card-container--clickable",
    ".artdeco-list li",
    "li.jobs-search-results__list-item",
]

print("\n--- Selector Results ---")
for sel in selectors:
    try:
        elements = driver.find_elements(By.CSS_SELECTOR, sel)
        if elements:
            print(f"✅ FOUND {len(elements)}: '{sel}'")
            print(f"   Text: {elements[0].text[:80]}")
        else:
            print(f"❌ Not found: '{sel}'")
    except Exception as e:
        print(f"❌ Error: '{sel}' → {e}")

time.sleep(3)
driver.quit()
