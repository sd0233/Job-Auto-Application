from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pickle
import time

options = Options()
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=options)

driver.get("https://www.linkedin.com/login")
print("=" * 50)
print("Login manually in the Chrome window that opened.")
print("After you are fully logged in press Enter here.")
print("=" * 50)
input()

pickle.dump(driver.get_cookies(), open("linkedin_cookies.pkl", "wb"))
print("✅ Cookies saved to linkedin_cookies.pkl")
driver.quit()
