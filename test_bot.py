import unittest
import asyncio
from database import Database
from telegram import Update, Chat, Message, User
from telegram.ext import ContextTypes
from unittest.mock import Mock, patch
import json
import logging
import os
import sys
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestMPesaBot(unittest.IsolatedAsyncioTestCase):  # Changed to IsolatedAsyncioTestCase
    def setUp(self):
        """Set up test environment"""
        # Use test database
        self.db = Database("test_mpesa_payments.db")
        self.test_user_id = 123456789
        self.test_group_id = 987654321
        
    def tearDown(self):
        """Clean up after tests"""
        # Remove test database
        if os.path.exists("test_mpesa_payments.db"):
            os.remove("test_mpesa_payments.db")

    def test_database_operations(self):
        """Test database operations"""
        logger.info("Testing database operations...")
        
        # Test adding payment
        payment_id = self.db.add_payment(
            user_id=self.test_user_id,
            username="test_user",
            amount=1000,
            phone_number="254722000000",
            group_id=self.test_group_id
        )
        self.assertIsNotNone(payment_id)
        logger.info("✅ Add payment test passed")

        # Test updating payment status
        success = self.db.update_payment_status(
            transaction_id="TEST123",
            status="completed"
        )
        self.assertTrue(success)
        logger.info("✅ Update payment status test passed")

        # Test getting total contributions
        total, contributors = self.db.get_total_contributions(self.test_group_id)
        self.assertEqual(total, 1000)
        self.assertEqual(contributors, 1)
        logger.info("✅ Get total contributions test passed")

    @patch('telegram.Bot')
    async def test_start_command_private(self, mock_bot):
        """Test start command in private chat"""
        logger.info("Testing start command in private chat...")
        
        # Mock private chat update
        update = Mock(spec=Update)
        update.effective_chat.type = 'private'
        update.effective_chat.id = self.test_user_id
        update.message = Mock(spec=Message)
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = mock_bot
        
        from telegram_bot import start
        result = await start(update, context)
        
        self.assertIsNotNone(result)
        self.assertTrue(update.message.reply_text.called)
        logger.info("✅ Start command private chat test passed")

    @patch('telegram.Bot')
    async def test_start_command_group(self, mock_bot):
        """Test start command in group chat"""
        logger.info("Testing start command in group chat...")
        
        # Mock group chat update
        update = Mock(spec=Update)
        update.effective_chat.type = 'group'
        update.effective_chat.id = self.test_group_id
        update.message = Mock(spec=Message)
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = mock_bot
        context.bot.username = "test_bot"
        
        from telegram_bot import start
        result = await start(update, context)
        
        self.assertIsNotNone(result)
        self.assertTrue(update.message.reply_text.called)
        logger.info("✅ Start command group chat test passed")

    async def test_payment_flow(self):
        """Test complete payment flow"""
        logger.info("Testing complete payment flow...")
        
        # Mock M-Pesa API response
        mock_mpesa_response = {
            "MerchantRequestID": "test-merchant-id",
            "CheckoutRequestID": "test-checkout-id",
            "ResponseCode": "0",
            "ResponseDescription": "Success"
        }
        
        with patch('mpesa_api.initiate_stk_push') as mock_stk_push:
            mock_stk_push.return_value = mock_mpesa_response
            
            # Simulate payment initiation
            payment_id = self.db.add_payment(
                user_id=self.test_user_id,
                username="test_user",
                amount=1000,
                phone_number="254722000000",
                group_id=self.test_group_id
            )
            
            self.assertIsNotNone(payment_id)
            logger.info("✅ Payment initiation test passed")
            
            # Simulate M-Pesa callback
            callback_data = {
                "Body": {
                    "stkCallback": {
                        "MerchantRequestID": "test-merchant-id",
                        "CheckoutRequestID": "test-checkout-id",
                        "ResultCode": 0,
                        "ResultDesc": "The service request is processed successfully."
                    }
                }
            }
            
            # Test callback handling
            from mpesa_callback_handler import mpesa_callback
            with patch('flask.request') as mock_request:
                mock_request.get_json.return_value = callback_data
                response = mpesa_callback()
                
                self.assertEqual(response[1], 200)
                logger.info("✅ Callback handling test passed")
            
            # Verify final payment status
            total, contributors = self.db.get_total_contributions(self.test_group_id)
            self.assertEqual(total, 1000)
            self.assertEqual(contributors, 1)
            logger.info("✅ Payment completion test passed")

def print_manual_test_instructions():
    """Print manual testing instructions"""
    instructions = """
    Manual Testing Instructions:
    
    1. Basic Bot Setup Test:
    - Send /start to the bot in private chat
    - Verify you receive the welcome message with Yes/No options
    
    2. Group Chat Test:
    - Add the bot to a group
    - Send /start in the group
    - Verify you receive the total contributions message and private chat button
    
    3. Payment Flow Test:
    - Click the private chat button from group
    - Start a payment process
    - Enter an amount (e.g., 10)
    - Enter a phone number (e.g., 254722000000)
    - Verify you receive the STK push on your phone
    
    4. Database Verification:
    - Use these SQL commands to check the database:
    
    sqlite3 mpesa_payments.db
    
    SELECT * FROM payments;  -- View all payments
    SELECT SUM(amount) FROM payments WHERE status='completed';  -- Check total
    SELECT COUNT(DISTINCT user_id) FROM payments;  -- Check unique contributors
    
    5. Common Issues:
    - If STK push fails, check:
        - Phone number format (should be 254XXXXXXXXX)
        - M-Pesa API credentials in config
        - Internet connection
        - Sandbox testing mode is active
    
    6. Logs Check:
    - Monitor the console for error messages
    - Check Flask server logs for callback processing
    
    7. Performance Test:
    - Try multiple payments in quick succession
    - Test with multiple users if possible
    - Verify group updates are timely
    """
    
    # Handle encoding issues by using sys.stdout.buffer.write()
    sys.stdout.buffer.write(instructions.encode('utf-8'))

if __name__ == '__main__':
    # Run automated tests
    logger.info("Starting automated tests...")
    unittest.main(verbosity=2, exit=False)
    
    # Print manual testing instructions
    print_manual_test_instructions()