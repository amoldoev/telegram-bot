import os
import logging
import requests
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv

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

async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello! I am alive. 🚀")

async def remindme(update: Update, context: CallbackContext) -> None:
    """Handle /remindme command."""
    await update.message.reply_text("Reminder set!")

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("remindme", remindme))

@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "🚀 Bot is running!"}), 200

@app.route("/webhook", methods=["POST"])
async def receive_update():
    try:
        update = request.get_json()
        if not update:
            return jsonify({"error": "No update received"}), 400

        print(f"📩 Received update: {update}")

        update_obj = Update.de_json(update, application.bot)

        if update_obj:
            await application.process_update(update_obj)  # Ensure async processing
        else:
            print("⚠️ Invalid update received:", update)
            return jsonify({"error": "Invalid update"}), 400

        return jsonify({"message": "✅ Update processed"}), 200

    except Exception as e:
        print(f"❌ Error in webhook: {e}")
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

async def run_application():
    """Ensure the bot is properly initialized before running."""
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

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
    set_webhook()  # Set webhook before running the app

    from hypercorn.asyncio import serve
    from hypercorn.config import Config

    config = Config()
    config.bind = ["0.0.0.0:10000"]  # Use port 10000

    loop = asyncio.get_event_loop()
    loop.create_task(run_application())  # ✅ Initialize the bot properly
    loop.run_until_complete(serve(app, config))  # ✅ Run Flask app asynchronously
