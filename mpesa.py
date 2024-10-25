import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime, timedelta

# Credentials from Safaricom Developer Portal
CONSUMER_KEY = '8W8PRqJXbb5f9uo80VA61uMlNd4IYCJ11MxxUAuTXh5JweTU'  # Replace with your actual consumer key
CONSUMER_SECRET = '4zEOTTWSez2XAUnXkbMzslr3XTCczWFHNN89wF7fUxMi2yepwjAV4kBGGz9reAFF'  # Replace with your actual consumer secret
SHORTCODE = '174379'  # Replace with your shortcode
PASSWORD = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # Replace with your password
CALLBACK_URL = 'https://hammtonndekebot.herokuapp.com/callback'  # Replace with your callback URL
BASE_URL = 'https://sandbox.safaricom.co.ke'  # Switch to production URL for live transactions

# Global variable to store access token and its expiration
access_token = None
token_expiry = None

def get_access_token():
    global access_token, token_expiry
    if access_token and token_expiry > datetime.now():
        return access_token  # Return the existing token if it's still valid
    
    # Generate a new access token if the previous one has expired or doesn't exist
    url = f"{BASE_URL}/oauth/v1/generate?grant_type=client_credentials"
    response = requests.get(url, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data['access_token']
        expires_in = token_data['expires_in']  # Typically 3600 seconds
        token_expiry = datetime.now() + timedelta(seconds=expires_in)
        return access_token
    else:
        print("Error generating access token:", response.json())
        return None
    
    
def initiate_stk_push(amount, phone_number):
    token = get_access_token()
    if token is None:
        return {"error": "Failed to generate access token"}

    url = f"{BASE_URL}/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": PASSWORD,
        "Timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),  # Generate current timestamp
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

# Example usage
if __name__ == "__main__":
    amount = 100  # Replace with the desired amount
    phone_number = "254792185625"  # Replace with the actual phone number
    response = send_stk_push(amount, phone_number)
    print(response)
