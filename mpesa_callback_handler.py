# File: mpesa_callback_handler.py
from flask import Flask, request, jsonify
from database import Database
import logging

app = Flask(__name__)
db = Database()
logger = logging.getLogger(__name__)

@app.route('/callback', methods=['POST'])
def mpesa_callback():
    """Handle M-Pesa callback"""
    try:
        callback_data = request.get_json()
        
        # Extract relevant information from callback
        result_code = callback_data.get('Body', {}).get('stkCallback', {}).get('ResultCode')
        transaction_id = callback_data.get('Body', {}).get('stkCallback', {}).get('CheckoutRequestID')
        
        if result_code == 0:  # Successful payment
            db.update_payment_status(transaction_id, 'completed')
            return jsonify({"status": "success"}), 200
        else:
            db.update_payment_status(transaction_id, 'failed')
            return jsonify({"status": "failed"}), 200
            
    except Exception as e:
        logger.error(f"Callback processing error: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500