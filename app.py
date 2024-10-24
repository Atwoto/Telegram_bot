from flask import Flask, request, jsonify
from mpesa import initiate_stk_push  # Importing the function from mpesa.py

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return "Payment Bot Backend is Running!", 200

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

if __name__ == '__main__':
    app.run(debug=True)
