from flask import Flask, request, jsonify
from mpesa import initiate_stk_push  # Importing the function from mpesa.py
import os
import requests

app = Flask(__name__)

# Route to check if the backend is running
@app.route('/', methods=['GET'])
def home():
    return "Payment Bot Backend is Running!", 200

# Route to manually trigger an STK Push
@app.route('/pay', methods=['POST'])
def pay():
    data = request.json
    phone_number = data.get('phone_number')
    amount = data.get('amount')
    
    if not phone_number or not amount:
        return jsonify({"error": "Phone number and amount are required"}), 400

    # Trigger STK Push
    response = initiate_stk_push(phone_number, amount)
    return jsonify(response)

# Telegram Webhook route
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if 'message' in data:
        chat_id = data['message']['chat']['id']
        text = data['message'].get('text', '')
        
        # If the command is /start, initiate the payment flow
        if text == '/start':
            # For testing, you can set a fixed phone number and amount
            phone_number = "254792185625"  # Replace with a valid phone number for testing
            amount = 10000  # Set the amount you want to charge for testing
            
            # Trigger STK Push
            response = initiate_stk_push(phone_number, amount)
            
            # Send a response back to the user on Telegram
            telegram_response = send_telegram_message(chat_id, "Payment Initiated! Please check your phone to confirm.")
            
            return jsonify({"mpesa_response": response, "telegram_response": telegram_response}), 200
    
    return "Webhook received", 200

# Function to send a message back to the user on Telegram
def send_telegram_message(chat_id, message):
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, json=payload)
    return response.json()

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True)
