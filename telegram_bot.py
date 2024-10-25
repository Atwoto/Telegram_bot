import os
import requests
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater
import logging

# Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN = '7390909460:AAHWLtjexjbJ2iZVweU0vqjJbwYhqxOohis'

# Initialize Telegram bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher
logging.basicConfig(level=logging.DEBUG)

# Command handler to start payment
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome! Send /pay to initiate a payment.')

# Handler to initiate payment
def pay(update: Update, context: CallbackContext):
    update.message.reply_text('Please provide your phone number (e.g., 2547XXXXXXXX) and the amount to pay in this format: phone_number,amount')
    return

# Message handler to receive phone number and amount
def handle_payment(update: Update, context: CallbackContext):
    user_input = update.message.text.split(',')
    if len(user_input) != 2:
        update.message.reply_text('Please provide the correct format: phone_number,amount')
        return

    phone_number = user_input[0].strip()
    amount = user_input[1].strip()

    # Make the payment request to your Flask server
    response = requests.post(
        'http://localhost:5000/pay',  # Or use the ngrok or production URL
        json={'phone_number': phone_number, 'amount': amount}
    )

    if response.status_code == 200:
        update.message.reply_text('Payment initiated! Please check your phone.')
    else:
        update.message.reply_text('Something went wrong. Please try again.')

# Register the handlers
dispatcher.add_handler(CommandHandler('start', start))
dispatcher.add_handler(CommandHandler('pay', pay))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_payment))

# Start webhook for production
if __name__ == "__main__":
    PORT = int(os.environ.get('PORT', 5000))
    updater.start_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path='webhook',
        webhook_url="https://hammtonndekebot.herokuapp.com/webhook"
    )
