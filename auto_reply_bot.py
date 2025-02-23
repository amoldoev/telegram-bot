import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Get bot token from environment variable
BOT_TOKEN = os.getenv("7520897863:AAEE290Wqy3gtLpn9lm34fVuuKquzhnsrHk")

# Function to handle the /start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! 👋 I am your bot. How can I assist you today?")

# Function to handle user messages with custom replies
async def reply(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()

    # Custom replies based on user messages
    if "hello" in user_message or "hi" in user_message:
        await update.message.reply_text("Hey there! 😊 How can I help you?")
    elif "how are you" in user_message:
        await update.message.reply_text("I'm just a bot, but I'm doing great! 😃 What about you?")
    elif "help" in user_message:
        await update.message.reply_text("Sure! You can ask me anything or type /start to see available options.")
    elif "bye" in user_message:
        await update.message.reply_text("Goodbye! Have a great day! 👋")
    else:
        await update.message.reply_text("I'm still learning! 🤖 Can you try something else?")

# Main function to start the bot using Webhooks (for Render deployment)
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", start))

    # Add message handler for text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))

    # Use Webhooks instead of polling
    PORT = int(os.environ.get("PORT", 8443))
    WEBHOOK_URL = f"https://{os.getenv('https://telegram-bot-agyv.onrender.com')}/{7520897863:AAEE290Wqy3gtLpn9lm34fVuuKquzhnsrHk}"

    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=WEBHOOK_URL
    )

if __name__ == "__main__":
    main()
