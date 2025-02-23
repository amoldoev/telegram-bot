from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Replace this with your bot token
BOT_TOKEN = "7520897863:AAEE290Wqy3gtLpn9lm34fVuuKquzhnsrHk"

# Function to handle the /start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Hello! 👋 I am your bot. How can I assist you today?")

# Function to handle user messages with custom replies
def reply(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()

    # Custom replies based on user messages
    if "hello" in user_message or "hi" in user_message:
        update.message.reply_text("Hey there! 😊 How can I help you?")
    elif "how are you" in user_message:
        update.message.reply_text("I'm just a bot, but I'm doing great! 😃 What about you?")
    elif "help" in user_message:
        update.message.reply_text("Sure! You can ask me anything or type /start to see available options.")
    elif "bye" in user_message:
        update.message.reply_text("Goodbye! Have a great day! 👋")
    else:
        update.message.reply_text("I'm still learning! 🤖 Can you try something else?")

# Main function to start the bot
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Add command handlers
    dp.add_handler(CommandHandler("start", start))

    # Add message handler for text messages
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, reply))

    # Start the bot
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
