import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from mpesa1 import initiate_stk_push
import logging
from typing import Dict

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Store user states
user_states: Dict[int, str] = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    logger.info(f"User {update.effective_user.id} started the bot")
    await update.message.reply_text("Welcome! Are you interested in contributing? (yes/no)")
    user_states[update.effective_user.id] = "awaiting_initial_response"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle user messages."""
    user_id = update.effective_user.id
    message = update.message.text.lower()
    state = user_states.get(user_id, "no_state")
    
    logger.info(f"Received message from user {user_id}: {message} (State: {state})")

    if state == "awaiting_initial_response":
        if message == "yes":
            await update.message.reply_text("Please enter the amount you wish to contribute (in KES):")
            user_states[user_id] = "awaiting_amount"
        elif message == "no":
            await update.message.reply_text("Thank you! If you change your mind, just type /start.")
            user_states.pop(user_id, None)
        else:
            await update.message.reply_text("Please respond with 'yes' or 'no'.")

    elif state == "awaiting_amount":
        try:
            amount = float(message)
            if amount <= 0:
                await update.message.reply_text("Please enter a valid amount greater than 0.")
                return

            # First, check if we have the required environment variables
            if not os.getenv('CONSUMER_KEY') or not os.getenv('CONSUMER_SECRET'):
                logger.error("Missing M-Pesa credentials in environment variables")
                await update.message.reply_text("Sorry, the payment system is not properly configured. Please contact the administrator.")
                return

            # For testing, using a default phone number
            phone_number = "254792185625"  # Replace with actual phone number logic
            
            logger.info(f"Initiating STK push for user {user_id}, amount: {amount}")
            
            try:
                # Initiate STK push with additional error handling
                await update.message.reply_text("Processing your payment request...")
                response = initiate_stk_push(phone_number, int(amount))
                logger.info(f"STK push response: {response}")
                
                if isinstance(response, dict):
                    if response.get('ResponseCode') == '0':
                        await update.message.reply_text("Payment request sent! Please check your phone to complete the transaction.")
                    else:
                        error_msg = response.get('ResponseDescription', 'Unknown error')
                        logger.error(f"STK push failed: {error_msg}")
                        await update.message.reply_text(f"Sorry, there was an error processing your request: {error_msg}")
                else:
                    logger.error(f"Unexpected response format: {response}")
                    await update.message.reply_text("Sorry, there was an unexpected error. Please try again later.")
            
            except Exception as e:
                logger.error(f"Error during STK push: {str(e)}", exc_info=True)
                await update.message.reply_text("Sorry, there was an error processing your payment. Please try again later.")
            
            user_states.pop(user_id, None)

        except ValueError:
            await update.message.reply_text("Please enter a valid number for the amount.")
    else:
        await update.message.reply_text("Please use /start to begin the contribution process.")

def main() -> None:
    """Start the bot."""
    try:
        # Get token from environment variable
        token = os.getenv('TELEGRAM_BOT_TOKEN')
        if not token:
            raise ValueError("No token found! Set your TELEGRAM_BOT_TOKEN environment variable.")

        # Verify M-Pesa credentials are set
        if not os.getenv('CONSUMER_KEY') or not os.getenv('CONSUMER_SECRET'):
            logger.warning("M-Pesa credentials not found in environment variables!")

        logger.info("Starting bot...")
        
        # Create the application
        application = Application.builder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

        # Start polling
        logger.info("Starting polling...")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)
        raise

if __name__ == '__main__':
    main()