import os
from flask import Flask, request
import requests
from telegram import Update
from telegram.ext import CommandHandler, MessageHandler, Filters, CallbackContext, Updater

app = Flask(__name__)

# Telegram bot token from BotFather
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')


# Flask route to handle Telegram webhooks
@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    # Get the data from the Telegram POST request
    update = Update.de_json(request.get_json(force=True), updater.bot)
    dispatcher.process_update(update)
    return "ok"

# Initialize Telegram bot
updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
dispatcher = updater.dispatcher

# Command handler to start payment
def start(update: Update, context: CallbackContext):
    update.message.reply_text('Welcome! Send /pay to initiate a payment.')

# Handler to initiate payment
def pay(update: Update, context: CallbackContext):
    # Here, get the phone number and amount from the user
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
        'http://localhost:5000/pay',  # Or use the ngrok URL
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
