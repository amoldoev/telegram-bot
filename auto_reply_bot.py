import os
import json
import asyncio
import logging
import requests
import pytz
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is missing! Check your environment variables.")

# File to store subscribed users
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
    save_subscribers()  # Save user list persistently

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

# Main function
async def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Register commands
    application.add_handler(CommandHandler("remindme", remind_me))

    # Scheduler setup
    scheduler = AsyncIOScheduler(timezone=pytz.UTC)
    scheduler.add_job(send_reminders, "interval", seconds=30)
    scheduler.start()

    logger.info("🚀 Bot is running...")
    await application.run_polling()

# Correct event loop handling
if __name__ == "__main__":
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None

    if loop and loop.is_running():
        loop.create_task(main())  # If an event loop is running, create a task
    else:
        asyncio.run(main())  # Otherwise, run normally
