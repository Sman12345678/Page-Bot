import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import messageHandler  # Import the message handler module
import time

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PREFIX = os.getenv("PREFIX", "/")

# Verification endpoint for Facebook webhook
@app.route('/webhook', methods=['GET'])
def verify():
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        logger.info("Webhook verification successful.")
        return request.args.get("hub.challenge")
    logger.error("Webhook verification failed: invalid verify token.")
    return "Verification failed", 403

# Main webhook endpoint to handle messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.info("Received data: %s", data)

    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                if "message" in event:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"].get("text")
                    message_attachments = event["message"].get("attachments")
                    message_command = event["message"].get("text")

                    # Check if message has text with a command prefix
                    if message_command and message_command.startswith(PREFIX):
                        response = messageHandler.handle_text_command(message_command[len(PREFIX):])
                        
                    
                    elif message_attachments:
                        response = messageHandler.handle_attachment(message_attachments)
                    elif message_text:
                        response = messageHandler.handle_text_message(message_text)
                    else:
                        response = "Sorry, I didn't understand that message."

                    # Send the response to the user
                    send_message(sender_id, response)
    return "EVENT_RECEIVED", 200

# Send message back to Facebook
def send_message(recipient_id, message_text):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post("https://graph.facebook.com/v21.0/me/messages", params=params, headers=headers, json=data)

    if response.status_code == 200:
        logger.info("Message sent successfully to user %s", recipient_id)
    else:
        logger.error("Failed to send message: %s", response.json())

# Test page access token validity
@app.before_request
def check_page_access_token():
    test_url = f"https://graph.facebook.com/me?access_token={PAGE_ACCESS_TOKEN}"
    response = requests.get(test_url)
    if response.status_code == 200:
        logger.info("Page access token is valid.")
    else:
        logger.error("Invalid page access token: %s", response.json())

start_time = time.time()

# Expose the start_time so CMD can access it
def get_bot_uptime():
    return time.time() - start_time





if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=3000)
