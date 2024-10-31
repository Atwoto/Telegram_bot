# File: mpesa_integration.py
import requests
import base64
from datetime import datetime
import logging
import json
from typing import Dict, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MpesaAPI:
    """Handles M-Pesa API integration"""
    
    def __init__(self):
        """Initialize M-Pesa API configurations"""
        # Load configurations from environment variables
        self.consumer_key = os.getenv('MPESA_CONSUMER_KEY')
        self.consumer_secret = os.getenv('MPESA_CONSUMER_SECRET')
        self.business_shortcode = os.getenv('MPESA_BUSINESS_SHORTCODE')
        self.passkey = os.getenv('MPESA_PASSKEY')
        self.callback_url = os.getenv('MPESA_CALLBACK_URL')
        
        # API endpoints
        self.auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        self.stkpush_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
        
        # For production, use these URLs instead:
        # self.auth_url = "https://api.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
        # self.stkpush_url = "https://api.safaricom.co.ke/mpesa/stkpush/v1/processrequest"

    def generate_access_token(self) -> str:
        """Generate OAuth access token"""
        try:
            # Create auth string and encode it
            auth_string = f"{self.consumer_key}:{self.consumer_secret}"
            auth_bytes = auth_string.encode('ascii')
            encoded_auth = base64.b64encode(auth_bytes).decode('ascii')

            headers = {
                'Authorization': f'Basic {encoded_auth}'
            }

            response = requests.get(self.auth_url, headers=headers)
            response.raise_for_status()  # Raise exception for non-200 status codes
            
            result = response.json()
            return result.get('access_token')

        except requests.exceptions.RequestException as e:
            logger.error(f"Error generating access token: {str(e)}")
            raise

    def generate_password(self) -> str:
        """Generate password for STK push"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        password_string = f"{self.business_shortcode}{self.passkey}{timestamp}"
        return base64.b64encode(password_string.encode('utf-8')).decode('utf-8')

    def initiate_stk_push(self, phone_number: str, amount: float) -> Dict[str, Any]:
        """
        Initiate STK push to the provided phone number
        
        Args:
            phone_number (str): Customer phone number (format: 254XXXXXXXXX)
            amount (float): Amount to be paid
            
        Returns:
            dict: Response from M-Pesa API
        """
        try:
            # Generate access token
            access_token = self.generate_access_token()
            
            # Generate password and timestamp
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            password = self.generate_password()

            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }

            payload = {
                "BusinessShortCode": self.business_shortcode,
                "Password": password,
                "Timestamp": timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": int(amount),  # Amount must be an integer
                "PartyA": phone_number,
                "PartyB": self.business_shortcode,
                "PhoneNumber": phone_number,
                "CallBackURL": self.callback_url,
                "AccountReference": "Payment",  # This can be customized
                "TransactionDesc": "Payment"    # This can be customized
            }

            response = requests.post(self.stkpush_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            if "ResponseCode" in result and result["ResponseCode"] == "0":
                return {
                    "success": True,
                    "checkout_request_id": result.get("CheckoutRequestID"),
                    "response_code": result.get("ResponseCode"),
                    "customer_message": result.get("CustomerMessage")
                }
            else:
                return {
                    "error": result.get("errorMessage", "Payment request failed"),
                    "response_code": result.get("ResponseCode")
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Error initiating STK push: {str(e)}")
            return {"error": "Failed to initiate payment. Please try again later."}
        except Exception as e:
            logger.error(f"Unexpected error during STK push: {str(e)}")
            return {"error": "An unexpected error occurred. Please try again later."}