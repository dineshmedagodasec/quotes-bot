import schedule
import time
from main import run_bot

# Post 3 times a day
schedule.every().day.at("07:00").do(run_bot)
schedule.every().day.at("12:00").do(run_bot)
schedule.every().day.at("19:00").do(run_bot)

print("🤖 Quotes Bot is running...")
print("📅 Scheduled at 7am, 12pm and 7pm daily")

while True:
    schedule.run_pending()
    time.sleep(60)