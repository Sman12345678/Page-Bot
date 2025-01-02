import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import requests
from io import BytesIO
import time
import messageHandler  # Custom module for handling commands and responses

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

                    # Check if the message starts with a command prefix
                    if message_text and message_text.startswith(PREFIX):
                        sliced_message = message_text[len(PREFIX):]
                        command_name = sliced_message.split()[0]
                        message = sliced_message[len(command_name):].strip()
                        response = messageHandler.handle_text_command(command_name, message)

                        # Handle image response
                        if isinstance(response, dict) and response.get("success"):
                            if isinstance(response["data"], BytesIO):  # Image response
                                upload_response = upload_image_to_graph(response["data"])
                                if upload_response.get("success"):
                                    send_message(sender_id, {"type": "image", "content": upload_response["attachment_id"]})
                                else:
                                    send_message(sender_id, {"type": "text", "content": "🚨 Failed to upload the image."})
                            else:
                                send_message(sender_id, {"type": "text", "content": response["data"]})
                        else:
                            send_message(sender_id, {"type": "text", "content": response})

                    elif message_attachments:
                        # Handle attachments
                        try:
                            attachment = message_attachments[0]
                            if attachment["type"] == "image":
                                image_url = attachment["payload"]["url"]
                                image_response = requests.get(image_url)
                                image_response.raise_for_status()
                                image_data = image_response.content
                                response = messageHandler.handle_attachment(image_data, attachment_type="image")
                                send_message(sender_id, {"type": "text", "content": response})
                        except Exception as e:
                            logger.error("Error handling attachment: %s", str(e))
                            send_message(sender_id, {"type": "text", "content": "🚨 Error processing attachment."})

                    elif message_text:
                        # Handle regular text message
                        response = messageHandler.handle_text_message(message_text)
                        send_message(sender_id, {"type": "text", "content": response})

                    else:
                        send_message(sender_id, {"type": "text", "content": "Sorry, I didn't understand that message."})

    return "EVENT_RECEIVED", 200

# Send message back to Facebook
def send_message(recipient_id, message=None, image_data=None, audio_data=None):
    params = {"access_token": PAGE_ACCESS_TOKEN}

    try:
        # Handle image message
        if image_data:
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

        # Handle audio message
        elif audio_data:
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

        # Handle text message
        elif message and isinstance(message, dict) and "type" in message and "content" in message:
            if message["type"] == "text":
                headers = {"Content-Type": "application/json"}
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": message["content"]},
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

# Function to upload image to Facebook Graph API
def upload_image_to_graph(image_data):
    try:
        params = {"access_token": PAGE_ACCESS_TOKEN}
        files = {"filedata": ("image.jpg", image_data, "image/jpeg")}
        response = requests.post(
            f"https://graph.facebook.com/v21.0/me/message_attachments",
            params=params,
            files=files
        )

        if response.status_code == 200:
            data = response.json()
            return {"success": True, "attachment_id": data.get("attachment_id")}
        else:
            return {"success": False, "data": response.json()}

    except Exception as e:
        logger.error("Failed to upload image: %s", str(e))
        return {"success": False, "data": f"🚨 Error: {str(e)}"}

# Start the server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
