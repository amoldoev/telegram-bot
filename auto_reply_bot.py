import os
import json
import logging
import requests
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Enable logging
logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Get bot token from environment variables
BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")  # For webhook
SUBSCRIBERS_FILE = "subscribers.json"

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is missing! Check your environment variables.")
if not RENDER_EXTERNAL_URL:
    raise ValueError("Error: RENDER_EXTERNAL_URL is missing! Set it in Render.")

# Load subscribers
def load_subscribers():
    try:
        with open(SUBSCRIBERS_FILE, "r") as file:
            return set(json.load(file))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

# Save subscribers
def save_subscribers():
    with open(SUBSCRIBERS_FILE, "w") as file:
        json.dump(list(subscribed_users), file)

# Track users who subscribed to reminders
subscribed_users = load_subscribers()

# /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! 👋 I am your bot. Type /remindme to receive reminders!")

# /remindme command
async def remind_me(update: Update, context: CallbackContext) -> None:
    chat_id = update.message.chat_id
    subscribed_users.add(chat_id)
    save_subscribers()

    logger.info(f"User {chat_id} subscribed for reminders.")
    await update.message.reply_text("✅ Reminder set! You'll receive a message every 30 seconds.")

# Send reminders
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

# Initialize and start the scheduler
scheduler = AsyncIOScheduler()
scheduler.add_job(lambda: asyncio.create_task(send_reminders()), "interval", seconds=30)
scheduler.start()

# Main function
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remindme", remind_me))

    # Webhook setup for Render
    PORT = int(os.getenv("PORT", 8443))
    WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}/{BOT_TOKEN}"

    logger.info("🚀 Bot is running with webhooks...")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
