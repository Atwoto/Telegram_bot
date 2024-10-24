import requests
from requests.auth import HTTPBasicAuth
import base64
from datetime import datetime
import json

# Your credentials from Safaricom Developer Portal
CONSUMER_KEY = '8W8PRqJXbb5f9uo80VA61uMlNd4IYCJ11MxxUAuTXh5JweTU' #Fill with your app Consumer Key
CONSUMER_SECRET = '4zEOTTWSez2XAUnXkbMzslr3XTCczWFHNN89wF7fUxMi2yepwjAV4kBGGz9reAFF'  #Fill with your app Secret
SHORTCODE = '174379'  # Use your business shortcode
PASSKEY = 'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919'
BASE_URL = 'https://sandbox.safaricom.co.ke'  # Change to the production URL when moving to live

def get_access_token():
    url = f'{BASE_URL}/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    json_response = response.json()
    return json_response['access_token']

def initiate_stk_push(phone_number, amount):
    access_token = get_access_token()
    api_url = f'{BASE_URL}/mpesa/stkpush/v1/processrequest'
    headers = {'Authorization': f'Bearer {access_token}'}

    # Generate a timestamp and the password required for STK Push
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    password = base64.b64encode(f'{SHORTCODE}{PASSKEY}{timestamp}'.encode()).decode('utf-8')

    # STK Push payload
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,  # User's phone number in 254 format
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": "https://yourdomain.com/callback",  # Update with your server's URL
        "AccountReference": "TestPayment",
        "TransactionDesc": "Payment for XYZ"
    }

    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()
