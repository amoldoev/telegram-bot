import os
import logging
import requests
import asyncio
import traceback
from flask import Flask, request, jsonify
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

# Ensure bot is initialized properly before use
async def initialize_bot():
    await application.initialize()

# Add command handlers
async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello! I am alive. 🚀")

async def remindme(update: Update, context: CallbackContext) -> None:
    """Handle /remindme command."""
    await update.message.reply_text("Reminder set!")

application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("remindme", remindme))

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🚀 Bot is running!"}), 200

@app.route("/webhook", methods=["POST"])
async def receive_update():
    """Receives Telegram updates via webhook and processes them asynchronously."""
    try:
        update = request.get_json()
        if not update:
            return jsonify({"error": "No update received"}), 400

        print(f"📩 Received update: {update}")
        update_obj = Update.de_json(update, application.bot)

        if update_obj:
            asyncio.create_task(application.process_update(update_obj))  # Non-blocking async call
        else:
            print("⚠️ Invalid update received:", update)
            return jsonify({"error": "Invalid update"}), 400

        return jsonify({"message": "✅ Update processed"}), 200

    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        traceback.print_exc()  # Print the full error stack trace
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

def set_webhook():
    """Set the webhook for Telegram Bot."""
    webhook_url = f"{WEBHOOK_URL}/webhook"
    response = requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
        json={"url": webhook_url},
    )
    if response.status_code == 200:
        print(f"✅ Webhook set successfully: {webhook_url}")
    else:
        print(f"❌ Failed to set webhook: {response.text}")

if __name__ == "__main__":
    print("🚀 Starting Flask server...")
    asyncio.run(initialize_bot())  # Ensure bot is initialized
    set_webhook()  # Set webhook before running the app

    from hypercorn.asyncio import serve  # ✅ Use Hypercorn for async support
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]  # Use port 10000
    asyncio.run(serve(app, config))  # ✅ Run Flask app asynchronously
