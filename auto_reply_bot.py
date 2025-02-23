import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Get bot token from environment variable
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN is missing! Check your environment variables.")

# Function to handle the /start command
async def start(update: Update, context) -> None:
    await update.message.reply_text("Hello! 👋 I am your bot. How can I assist you today?")

# Function to handle user messages with custom replies
async def reply(update: Update, context) -> None:
    user_message = update.message.text.lower()

    # Custom replies based on user messages
    responses = {
        "hello": "Hey there! 😊 How can I help you?",
        "hi": "Hey there! 😊 How can I help you?",
        "how are you": "I'm just a bot, but I'm doing great! 😃 What about you?",
        "help": "Sure! You can ask me anything or type /start to see available options.",
        "bye": "Goodbye! Have a great day! 👋"
    }

    # Send appropriate response or default message
    response = responses.get(user_message, "I'm still learning! 🤖 Can you try something else?")
    await update.message.reply_text(response)

# Main function to start the bot using Webhooks (for Render deployment)
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))

    # Add message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # Use Webhooks instead of polling
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = f"{os.getenv('RENDER_EXTERNAL_URL')}/{BOT_TOKEN}"

    if not os.getenv('RENDER_EXTERNAL_URL'):
        raise ValueError("Error: RENDER_EXTERNAL_URL is missing! Ensure it's set in Render.")

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,  # Security: Keeps webhook URL unique
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
