import os
import logging
import requests
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv  # Load .env variables

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

if not BOT_TOKEN or not WEBHOOK_URL:
    raise ValueError("❌ Error: BOT_TOKEN or WEBHOOK_URL is missing! Check your .env file.")

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

@app.route(f"/{BOT_TOKEN}/webhook", methods=["POST"])
def receive_update():
    """Receives Telegram updates via webhook."""
    update = request.get_json()
    print(f"📩 Received update: {update}")  # 🔥 DEBUGGING LOG
    
    if update:
        update_obj = Update.de_json(update, application.bot)
        application.process_update(update_obj)
        return "OK", 200
    else:
        return "❌ No update received", 400


async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello! I am alive. 🚀")

async def remindme(update: Update, context: CallbackContext) -> None:
    """Handle /remindme command."""
    await update.message.reply_text("Reminder set!")

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("remindme", remindme))

def set_webhook():
    """Set the webhook for Telegram Bot."""
    webhook_url = f"{WEBHOOK_URL}/{BOT_TOKEN}/webhook"  # 🔥 FIXED webhook path
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": webhook_url},
    )
    if response.status_code == 200:
        print(f"✅ Webhook set successfully: {webhook_url}")
    else:
        print(f"❌ Failed to set webhook: {response.text}")

if __name__ == "__main__":
    # Set the webhook before running the bot
    set_webhook()
    
    # Start the Flask server
    PORT = int(os.environ.get("PORT", 10000))  # Default to port 10000
    app.run(host="0.0.0.0", port=PORT)
