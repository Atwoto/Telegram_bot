# File: test_mpesa.py
import logging
from mpesa_api import initiate_stk_push
import json

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_mpesa_integration():
    """Test M-Pesa integration"""
    try:
        # Test phone number and amount
        test_phone = "254792185625"  # Replace with your test phone number
        test_amount = 1  # Minimum amount for testing
        
        logger.info("Initiating STK Push...")
        response = initiate_stk_push(test_phone, test_amount)
        
        logger.info(f"STK Push Response: {json.dumps(response, indent=2)}")
        
        if "error" not in response:
            logger.info("✅ STK Push initiated successfully!")
            logger.info(f"Merchant Request ID: {response.get('MerchantRequestID')}")
            logger.info(f"Checkout Request ID: {response.get('CheckoutRequestID')}")
            return True
        else:
            logger.error(f"❌ STK Push failed: {response.get('error')}")
            return False

    except Exception as e:
        logger.error(f"❌ Test failed with error: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting M-Pesa integration test...")
    success = test_mpesa_integration()
    
    if success:
        logger.info("✅ All tests passed successfully!")
    else:
        logger.error("❌ Tests failed. Please check the logs above for details.")