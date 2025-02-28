import os
import logging
import asyncio
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("Error: BOT_TOKEN or WEBHOOK_URL is missing! Check your .env file.")

print(f"✅ Bot Token Loaded: {BOT_TOKEN[:5]}...")  # Confirm token loading

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Telegram Bot Application
application = Application.builder().token(BOT_TOKEN).build()


@app.route("/")
def home():
    return "🚀 Bot is running!", 200


@app.route(f"/webhook", methods=["POST"])  # 🔥 FIXED route
def receive_update():
    """Receives Telegram updates via webhook."""
    try:
        update = Update.de_json(request.get_json(), application.bot)
        application.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Error processing update: {str(e)}")
        return "Error", 500


async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello! I am alive.")


async def remindme(update: Update, context: CallbackContext) -> None:
    """Handle /remindme command."""
    await update.message.reply_text("Reminder set!")


# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("remindme", remindme))


async def start_bot():
    """Start the bot and set up webhook."""
    await application.initialize()
    await application.start()
    await application.updater.start_polling()


def set_webhook():
    """Set the webhook for Telegram Bot."""
    webhook_url = f"{WEBHOOK_URL}/webhook"  # 🔥 FIXED webhook path
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": webhook_url},
    )
    if response.status_code == 200:
        print(f"✅ Webhook set successfully: {webhook_url}")
    else:
        print(f"❌ Failed to set webhook: {response.text}")


if __name__ == "__main__":
    set_webhook()  # Automatically set webhook on startup
    PORT = int(os.environ.get("PORT", 10000))  # Default to port 10000
    asyncio.run(start_bot())  # Run bot in async mode
    app.run(host="0.0.0.0", port=PORT, threaded=True)  # Flask server
