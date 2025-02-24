import logging
import requests
import os
import json
import asyncio
import pytz
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is missing! Check your environment variables.")

# File to store subscribed users (persistent storage)
SUBSCRIBERS_FILE = "subscribers.json"

# Load subscribed users from file
def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Save subscribed users to file
def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w") as file:
        json.dump(list(subscribed_users), file)

# Initialize subscribed users
subscribed_users = load_subscribers()

# Function to handle /remindme command
async def remind_me(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    subscribed_users.add(chat_id)
    save_subscribers()  # Save users persistently

    logger.info(f"User {chat_id} subscribed for reminders.")
    await update.message.reply_text("✅ Reminder set! You'll receive a notification every 30 seconds.")

# Function to send reminders
async def send_reminders():
    logger.info("🚀 Sending reminders...")
    for chat_id in subscribed_users:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": "🔔 Reminder! This repeats every 30 seconds."}
            response = requests.post(url, json=payload)

            if response.status_code == 200:
                logger.info(f"✅ Sent reminder to {chat_id}")
            else:
                logger.error(f"❌ Failed to send reminder to {chat_id}: {response.text}")

        except Exception as e:
            logger.error(f"❌ Error sending reminder to {chat_id}: {e}")

# Set timezone explicitly to avoid errors
TIMEZONE = pytz.utc  # Change to your preferred timezone, e.g., pytz.timezone('America/New_York')

# Scheduler setup (Runs every 30 seconds)
scheduler = AsyncIOScheduler(timezone=TIMEZONE)
scheduler.start()

async def schedule_reminders():
    while True:
        await send_reminders()
        await asyncio.sleep(30)  # Repeat every 30 seconds

# Main function
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("remindme", remind_me))

    logger.info("🚀 Bot is running...")

    # Start reminder task
    asyncio.create_task(schedule_reminders())

    # Run bot in polling mode (make sure webhook is deleted first)
    await application.bot.delete_webhook()  # Ensure webhook is removed before polling
    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
