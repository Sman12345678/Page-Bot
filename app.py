import os
import logging
from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS
import telegram
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import messageHandler  # Import the message handler module
import time

# Load environment variables
load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME", "my_telegram_bot")
PREFIX = os.getenv("PREFIX", "/")

# Initialize Telegram bot
bot = telegram.Bot(token=TELEGRAM_TOKEN)

# Start time tracking
start_time = time.time()


def get_bot_uptime():
    return time.time() - start_time


# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /start command."""
    user = update.effective_user
    await update.message.reply_text(f"Hello, {user.first_name}! I am your bot, ready to assist you!")


async def uptime(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles the /uptime command."""
    uptime = get_bot_uptime()
    await update.message.reply_text(f"I have been running for {uptime:.2f} seconds.")


# Message Handlers
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles text messages."""
    message = update.message.text

    # Check if message is a command
    if message.startswith(PREFIX):
        command = message[len(PREFIX):]
        response = messageHandler.handle_text_command(command)
    else:
        response = messageHandler.handle_text_message(message)

    await update.message.reply_text(response)


async def handle_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles unknown commands."""
    await update.message.reply_text("Sorry, I didn't understand that command.")


# Initialize Telegram bot application
app_telegram = Application.builder().token(TELEGRAM_TOKEN).build()

# Add handlers to the bot
app_telegram.add_handler(CommandHandler("start", start))
app_telegram.add_handler(CommandHandler("uptime", uptime))
app_telegram.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app_telegram.add_handler(MessageHandler(filters.COMMAND, handle_unknown))


# Flask route to set webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    """Handles Telegram webhook updates."""
    json_data = request.get_json()
    update = Update.de_json(json_data, bot)
    app_telegram.process_update(update)
    return "EVENT_RECEIVED", 200


if __name__ == '__main__':
    # Start the Flask app
    webhook_url = os.getenv("WEBHOOK_URL", "https://your-server-url/webhook")
    bot.set_webhook(url=webhook_url)
    app.run(debug=True, host='0.0.0.0', port=3000)
