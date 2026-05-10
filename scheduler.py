import schedule
import time
import subprocess
from utils.logger import get_logger

logger = get_logger()

def run_bot():
    logger.info("Scheduler triggering bot run...")
    subprocess.run(["python", "main.py"])
    logger.info("Bot run complete. Next run tomorrow at 09:00.")

# Run every day at 9 AM
schedule.every().day.at("09:00").do(run_bot)

logger.info("Scheduler started. Bot will run daily at 09:00 AM.")
logger.info("Press Ctrl+C to stop.")

while True:
    schedule.run_pending()
    time.sleep(60)