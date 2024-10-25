import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime
import json


# Replace with your actual credentials and parameters
ACCESS_TOKEN = 'your_access_token'  # Replace with your actual access token
SHORTCODE = 'y174379'  # Replace with your shortcode
PASSWORD = "MTc0Mzc5YmZiMjc5ZjlhYTliZGJjZjE1OGU5N2RkNzFhNDY3Y2QyZTBjODkzMDU5YjEwZjc4ZTZiNzJhZGExZWQyYzkxOTIwMTYwMjE2MTY1NjI3"  # Replace with your password
TIMESTAMP = "20160216165627",  # Generate timestamp as required
CALLBACK_URL = '"https://hammtonndekebot.herokuapp.com/callback"'  # Replace with your callback URL



# Credentials from Safaricom Developer Portal
CONSUMER_KEY = '8W8PRqJXbb5f9uo80VA61uMlNd4IYCJ11MxxUAuTXh5JweTU'
CONSUMER_SECRET = '4zEOTTWSez2XAUnXkbMzslr3XTCczWFHNN89wF7fUxMi2yepwjAV4kBGGz9reAFF'
SHORTCODE = ''  # Use your business shortcode
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
BASE_URL = 'https://sandbox.safaricom.co.ke'  # Switch to production URL for live transactions

def send_stk_push(amount, phone_number):
    url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": "Bearer " + ACCESS_TOKEN,
        "Content-Type": "application/json",
    }
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": PASSWORD,
        "Timestamp": TIMESTAMP,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "Contribution",
        "TransactionDesc": "Contributing to the cause",
    }
    
    response = requests.post(url, json=payload, headers=headers)
    return response.json()