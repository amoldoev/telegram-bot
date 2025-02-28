import os
import logging
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Load environment variables
TOKEN = os.getenv("BOT_TOKEN")  # Telegram Bot Token
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # Your Render Webhook URL

# Initialize Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Telegram Bot Application
application = Application.builder().token(TOKEN).build()

@app.route("/")
def home():
    return "Bot is running!", 200

@app.route(f"/{TOKEN}", methods=["POST"])
def receive_update():
    """Receives Telegram updates via webhook."""
    update = Update.de_json(request.get_json(), application.bot)
    application.process_update(update)
    return "OK", 200

async def start(update: Update, context: CallbackContext) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello! I am alive.")

async def remindme(update: Update, context: CallbackContext) -> None:
    """Handle /remindme command."""
    await update.message.reply_text("Reminder set!")

# Add command handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("remindme", remindme))

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))  # Default to port 10000
    app.run(host="0.0.0.0", port=PORT)
