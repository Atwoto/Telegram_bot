from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from database import Database
import logging
import re
from mpesa_integration import MpesaAPI

# Initialize M-Pesa API
mpesa_api = MpesaAPI()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

# Define conversation states
CONFIRM_PAYMENT, AMOUNT, PHONE_NUMBER, REDIRECT_TO_PRIVATE = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and handle group/private chat differently"""
    if update.effective_chat.type != 'private':
        # In group chat, send a button to start private chat
        bot_username = context.bot.username
        start_button = InlineKeyboardButton(
            "Start Private Payment",
            url=f"https://t.me/{bot_username}?start=from_group_{update.effective_chat.id}"
        )
        keyboard = InlineKeyboardMarkup([[start_button]])
        
        # Show total contributions for the group
        total, contributors = db.get_total_contributions(update.effective_chat.id)
        
        await update.message.reply_text(
            f"💰 Total Contributions: KES {total:,.2f}\n"
            f"👥 Total Contributors: {contributors}\n\n"
            "Click below to make a private payment:",
            reply_markup=keyboard
        )
        return ConversationHandler.END
    
    # In private chat, proceed with payment
    reply_keyboard = [['Yes', 'No']]
    await update.message.reply_text(
        'Welcome to the M-Pesa Payment Bot! 🤖\n\n'
        'Would you like to make a payment?',
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder='Yes or No?'
        ),
    )
    
    # Extract group_id if payment was initiated from a group
    if context.args and context.args[0].startswith('from_group_'):
        context.user_data['group_id'] = int(context.args[0].split('_')[2])
    
    return CONFIRM_PAYMENT

async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the user's response to whether they want to make a payment."""
    user_response = update.message.text
    
    if user_response == 'No':
        await update.message.reply_text(
            'Payment cancelled. You can start a new payment anytime with /start',
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        'Please enter the amount you want to pay in KES (e.g., 100):',
        reply_markup=ReplyKeyboardRemove(),
    )
    return AMOUNT

async def handle_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the amount entered by the user."""
    try:
        amount = float(update.message.text)
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Store amount in context
        context.user_data['amount'] = amount
        
        await update.message.reply_text(
            f'Amount set to KES {amount:,.2f}\n\n'
            'Please enter your M-Pesa phone number:\n'
            '(Format: 254XXXXXXXXX or 07XXXXXXXX or 01XXXXXXXX)'
        )
        return PHONE_NUMBER
    
    except ValueError:
        await update.message.reply_text(
            'Please enter a valid amount (numbers only, greater than 0).'
        )
        return AMOUNT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation."""
    await update.message.reply_text(
        'Payment cancelled. You can start a new payment anytime with /start',
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END

async def handle_phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle the phone number and initiate payment."""
    phone_number = update.message.text.strip()
    
    if not re.match(r'^(254|\+254|0)\d{9}$', phone_number):
        await update.message.reply_text(
            'Invalid phone number format. Please enter your phone number as:\n'
            '254XXXXXXXXX or 07XXXXXXXX or 01XXXXXXXX'
        )
        return PHONE_NUMBER
    
    # Format phone number
    if phone_number.startswith('0'):
        phone_number = '254' + phone_number[1:]
    elif phone_number.startswith('+'):
        phone_number = phone_number[1:]

    amount = context.user_data['amount']
    group_id = context.user_data.get('group_id')
    
    # Store payment information in database
    payment_id = db.add_payment(
        user_id=update.effective_user.id,
        username=update.effective_user.username or update.effective_user.first_name,
        amount=amount,
        phone_number=phone_number,
        group_id=group_id
    )
    
    await update.message.reply_text(
        f'Processing payment...\n'
        f'Amount: KES {amount:,.2f}\n'
        f'Phone: {phone_number}\n\n'
        'Please wait...'
    )

    try:
        # Initiate STK push using the MpesaAPI instance
        response = mpesa_api.initiate_stk_push(phone_number, amount)
        
        if response.get("success", False):
            await update.message.reply_text(
                '✅ Payment request sent successfully!\n\n'
                f'Checkout ID: {response.get("checkout_request_id")}\n'
                f'Message: {response.get("customer_message", "Please check your phone for the STK push prompt.")}\n\n'
                'Enter your PIN to complete the payment.\n\n'
                'Use /start to make another payment.'
            )
            
            # If payment was from a group, send update to group
            if group_id:
                total, contributors = db.get_total_contributions(group_id)
                await context.bot.send_message(
                    chat_id=group_id,
                    text=f"💫 New contribution initiated!\n\n"
                         f"💰 Total Contributions: KES {total:,.2f}\n"
                         f"👥 Total Contributors: {contributors}"
                )
        else:
            error_message = response.get("error", "Unknown error")
            logger.error(f"Payment failed: {error_message}")
            await update.message.reply_text(
                f'❌ Payment request failed: {error_message}\n\n'
                'Please try again later or contact support.\n\n'
                'Use /start to try again.'
            )
    
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        await update.message.reply_text(
            '❌ An error occurred while processing your payment.\n\n'
            'Please try again later or contact support.\n\n'
            'Use /start to try again.'
        )

    return ConversationHandler.END

def main() -> None:
    """Run the bot."""
    # Initialize bot with your token
    application = Application.builder().token("7390909460:AAHWLtjexjbJ2iZVweU0vqjJbwYhqxOohis").build()

    # Create a list of command handlers for all variations
    start_commands = ['start', 'contribute', 'changa', 'ongeza', 'donate']
    command_handlers = [CommandHandler(cmd, start) for cmd in start_commands]

    # Add conversation handler with the states
    conv_handler = ConversationHandler(
        entry_points=command_handlers,
        states={
            CONFIRM_PAYMENT: [MessageHandler(filters.Regex('^(Yes|No)$'), handle_payment_confirmation)],
            AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amount)],
            PHONE_NUMBER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone_number)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    
    # Start the bot
    logger.info("Bot started successfully!")
    application.run_polling()

if __name__ == '__main__':
    main()