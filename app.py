import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import time
from io import BytesIO

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

start_time = time.time()

def get_bot_uptime():
    return time.time() - start_time

# Verification endpoint for Facebook webhook
@app.route('/webhook', methods=['GET'])
def verify():
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        logger.info("Webhook verification successful.")
        return request.args.get("hub.challenge", "")
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

                    # Handle command messages
                    if message_text and message_text.startswith(PREFIX):
                        sliced_message = message_text[len(PREFIX):]
                        command_name = sliced_message.split()[0]
                        message = sliced_message[len(command_name):].strip()
                        response = handle_command(command_name, message)

                        if isinstance(response, dict) and response.get("success"):
                            if isinstance(response["data"], BytesIO):  # Image response
                                send_message(sender_id, image_data=response["data"])
                            else:
                                send_message(sender_id, {"type": "text", "content": response["data"]})
                        else:
                            send_message(sender_id, {"type": "text", "content": response.get("data", "Error occurred.")})

                    elif message_text:  # Handle text messages
                        send_message(sender_id, {"type": "text", "content": "Command not recognized."})

                    elif message_attachments:  # Handle attachments
                        send_message(sender_id, {"type": "text", "content": "Attachments are not supported."})

    return "EVENT_RECEIVED", 200

# Handle specific commands
def handle_command(command_name, message):
    if command_name == "uptime":
        uptime = get_bot_uptime()
        return {"success": True, "data": f"Bot has been running for {uptime:.2f} seconds."}
    elif command_name == "test":
        return {"success": True, "data": "Test command executed successfully."}
    else:
        return {"success": False, "data": f"Unknown command: {command_name}"}

# Send a message back to the user
def send_message(recipient_id, message=None, image_data=None, audio_data=None):
    params = {"access_token": PAGE_ACCESS_TOKEN}

    try:
        if image_data:  # Handle image messages
            files = {
                "recipient": f'{{"id":"{recipient_id}"}}',
                "message": '{"attachment":{"type":"image", "payload":{}}}',
                "filedata": ("image.jpg", image_data, "image/jpeg"),
            }
            response = requests.post(
                f"https://graph.facebook.com/v21.0/me/messages",
                params=params,
                files=files
            )

        elif audio_data:  # Handle audio messages
            files = {
                "recipient": f'{{"id":"{recipient_id}"}}',
                "message": '{"attachment":{"type":"audio", "payload":{}}}',
                "filedata": ("audio.mp3", audio_data, "audio/mpeg"),
            }
            response = requests.post(
                f"https://graph.facebook.com/v21.0/me/messages",
                params=params,
                files=files
            )

        elif message and isinstance(message, dict) and "type" in message and "content" in message:
            if message["type"] == "text":
                headers = {"Content-Type": "application/json"}
                text_content = message["content"]

                # Ensure text content is a valid UTF-8 string
                if isinstance(text_content, str):
                    text_content = text_content.encode("utf-8").decode("utf-8")

                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": text_content},
                }
                response = requests.post(
                    f"https://graph.facebook.com/v21.0/me/messages",
                    params=params,
                    headers=headers,
                    json=data
                )
            else:
                raise ValueError(f"Unsupported message type: {message['type']}")

        else:
            raise ValueError("Invalid message format or missing data.")

        # Check response status
        if response.status_code == 200:
            logger.info("Message sent successfully to user %s", recipient_id)
        else:
            try:
                logger.error("Failed to send message: %s", response.json())
            except Exception:
                logger.error("Failed to send message. Status code: %d", response.status_code)

    except Exception as e:
        logger.error("Error sending message: %s", str(e))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
