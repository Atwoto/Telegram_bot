# File: mpesa_config.py
class MpesaConfig:
    # Safaricom API credentials
    CONSUMER_KEY = "8W8PRqJXbb5f9uo80VA61uMlNd4IYCJ11MxxUAuTXh5JweTU"  # Replace with your key
    CONSUMER_SECRET = "4zEOTTWSez2XAUnXkbMzslr3XTCczWFHNN89wF7fUxMi2yepwjAV4kBGGz9reAFF"  # Replace with your secret
    BUSINESS_SHORTCODE = "174379"  # Default test shortcode
    PASSKEY = "bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919"  # Default test passkey

     # API URLs
    AUTH_URL = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    STK_PUSH_URL = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    CALLBACK_URL = "https://hammtonndekebot.herokuapp.com/callback"  # Replace with your callback URL
