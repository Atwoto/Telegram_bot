from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from mpesa import send_stk_push  # Import the STK push function from mpesa.py

# To store user data temporarily
user_data = {}

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text("Welcome! Are you interested in contributing? (yes/no)")

def handle_response(update: Update, context: CallbackContext) -> None:
    user_response = update.message.text.lower()
    
    if user_response == "yes":
        update.message.reply_text("Please enter the amount you wish to contribute:")
        return  # Wait for user to provide an amount
    elif user_response == "no":
        update.message.reply_text("Thank you! If you change your mind, just type /start.")
    else:
        update.message.reply_text("Please respond with 'yes' or 'no'.")

def handle_amount(update: Update, context: CallbackContext) -> None:
    try:
        amount = float(update.message.text)
        user_phone = update.message.from_user.phone_number  # Assuming you've captured the user's phone number
        response = send_stk_push(amount, user_phone)

        # Check response and send appropriate message
        if response.get('ResponseCode') == '0':
            update.message.reply_text("STK Push request sent successfully! Please check your phone.")
        else:
            update.message.reply_text(f"Error: {response.get('ResponseDescription')}")
    except ValueError:
        update.message.reply_text("Please enter a valid amount.")

def main() -> None:
    updater = Updater("your_telegram_bot_token")  # Replace with your bot token
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_response))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_amount))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
