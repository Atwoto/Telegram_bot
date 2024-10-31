# File: mpesa_utils.py
import os
import base64
import requests
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class MpesaAPI:
    def __init__(self):
        # Safaricom API credentials - you'll need to get these from Safaricom Developer Portal
        self.consumer_key = "8W8PRqJXbb5f9uo80VA61uMlNd4IYCJ11MxxUAuTXh5JweTU"  # Replace with your key
        self.consumer_secret = "4zEOTTWSez2XAUnXkbMzslr3XTCczWFHNN89wF7fUxMi2yepwjAV4kBGGz9reAFF"  # Replace with your secret
        self.business_shortcode = "174379"  # Default test shortcode
        self.passkey = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # Default test passkey
        
        # API URLs - using sandbox URLs for testing
        self.auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stk_push_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    def generate_auth_token(self):
        """Generate authentication token"""
        try:
            # Encode credentials
            auth_str = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_str.encode('ascii')
            base64_auth = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                'Authorization': f'Basic {base64_auth}'
            }

            response = requests.get(self.auth_url, headers=headers)
            
            if response.status_code == 200:
                token = response.json()['access_token']
                logger.info("Successfully generated access token")
                return token
            else:
                logger.error(f"Failed to generate access token: {response.text}")
                return None

        except Exception as e:
            logger.error(f"Error generating auth token: {str(e)}")
            return None

    def generate_password(self):
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        str_to_encode = f"{self.business_shortcode}{self.passkey}{timestamp}"
        encoded = base64.b64encode(str_to_encode.encode()).decode('utf-8')
        return encoded, timestamp

    def initiate_stk_push(self, phone_number, amount):
        """Initiate STK Push transaction"""
        try:
            access_token = self.generate_auth_token()
            if not access_token:
                return {"error": "Failed to generate access token"}

            # Generate password and timestamp
            password, timestamp = self.generate_password()

            # Format phone number (remove leading 0 or +254)
            if phone_number.startswith('+'):
                phone_number = phone_number[1:]
            if phone_number.startswith('0'):
                phone_number = '254' + phone_number[1:]

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": amount,
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": "https://hammtonndekebot.herokuapp.com/callback",  # Replace with your callback URL
                "AccountReference": "Test Payment",
                "TransactionDesc": "Test Payment" 
            }

            response = requests.post(self.stk_push_url, json=payload, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "error": f"STK push failed: {response.text}",
                    "status_code": response.status_code
                }

        except Exception as e:
            logger.error(f"Error in STK push: {str(e)}")
            return {"error": str(e)}

# File: test_mpesa.py
import logging

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def test_mpesa_integration():
    """Test M-Pesa integration"""
    try:
        # Initialize MpesaAPI
        mpesa = MpesaAPI()
        
        # Test phone number and amount
        test_phone = "254792185625"  # Replace with your test phone number
        test_amount = 1  # Minimum amount for testing
        
        logger.info("Initiating STK Push...")
        response = mpesa.initiate_stk_push(test_phone, test_amount)
        
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