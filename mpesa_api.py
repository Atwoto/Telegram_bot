# File: mpesa_api.py
import base64
import requests
from datetime import datetime
import logging
from mpesa_config import MpesaConfig

logger = logging.getLogger(__name__)

def generate_auth_token():
    """Generate authentication token"""
    try:
        auth_str = f"{MpesaConfig.CONSUMER_KEY}:{MpesaConfig.CONSUMER_SECRET}"
        auth_bytes = auth_str.encode('ascii')
        base64_auth = base64.b64encode(auth_bytes).decode('ascii')

        headers = {
            'Authorization': f'Basic {base64_auth}'
        }

        response = requests.get(MpesaConfig.AUTH_URL, headers=headers)
        
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

def generate_password():
    """Generate password for STK push"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    str_to_encode = f"{MpesaConfig.BUSINESS_SHORTCODE}{MpesaConfig.PASSKEY}{timestamp}"
    encoded = base64.b64encode(str_to_encode.encode()).decode('utf-8')
    return encoded, timestamp

def initiate_stk_push(phone_number, amount):
    """Initiate STK Push transaction"""
    try:
        access_token = generate_auth_token()
        if not access_token:
            return {"error": "Failed to generate access token"}

        # Generate password and timestamp
        password, timestamp = generate_password()

        # Format phone number
        if phone_number.startswith('+'):
            phone_number = phone_number[1:]
        if phone_number.startswith('0'):
            phone_number = '254' + phone_number[1:]

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }

        payload = {
            "BusinessShortCode": MpesaConfig.BUSINESS_SHORTCODE,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone_number,
            "PartyB": MpesaConfig.BUSINESS_SHORTCODE,
            "PhoneNumber": phone_number,
            "CallBackURL": MpesaConfig.CALLBACK_URL,
            "AccountReference": "Test Payment",
            "TransactionDesc": "Test Payment" 
        }

        response = requests.post(MpesaConfig.STK_PUSH_URL, json=payload, headers=headers)
        
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