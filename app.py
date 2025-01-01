import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import messageHandler  # Import the message handler module
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

# Function to upload an image to Facebook's Graph API
def upload_image_to_graph(image_data):
    """
    Uploads an image to the Facebook Graph API and returns the attachment ID.
    """
    url = f"https://graph.facebook.com/v21.0/me/message_attachments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    files = {
        "filedata": ("image.jpg", image_data, "image/jpeg"),
    }
    try:
        response = requests.post(url, params=params, files=files)
        if response.status_code == 200:
            result = response.json()
            return {"success": True, "attachment_id": result.get("attachment_id")}
        else:
            logger.error("Failed to upload image: %s", response.json())
            return {"success": False, "error": response.json()}
    except Exception as e:
        logger.error("Error in upload_image_to_graph: %s", str(e))
        return {"success": False, "error": str(e)}

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
                    message_command = event["message"].get("text")

                    # Check if message has text with a command prefix
                    if message_command and message_command.startswith(PREFIX):
                        sliced_message = message_command[len(PREFIX):]
                        command_name = sliced_message.split()[0]
                        message = sliced_message[len(command_name):].strip()
                        response = messageHandler.handle_text_command(command_name, message)

                        # Handle image response
                        if isinstance(response, dict) and response.get("success"):
                            if isinstance(response["data"], BytesIO):  # Check if the response is an image
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
                        try:
                            # Extract the URL of the first attachment
                            attachment = message_attachments[0]
                            if attachment["type"] == "image":
                                image_url = attachment["payload"]["url"]

                                # Download the image data
                                try:
                                    image_response = requests.get(image_url)
                                    image_response.raise_for_status()
                                    image_data = image_response.content
                                    # Send the image data to messageHandler
                                    response = messageHandler.handle_attachment(image_data, attachment_type="image")
                                    send_message(sender_id, {"type": "text", "content": response})
                                except requests.exceptions.RequestException as e:
                                    logger.error("Failed to download image: %s", str(e))
                                    response = "Failed to process the image attachment."
                                    send_message(sender_id, {"type": "text", "content": response})
                        except Exception as e:
                            logger.error("Error handling attachment: %s", str(e))
                            response = "Error processing attachment."
                            send_message(sender_id, {"type": "text", "content": response})

                    elif message_text:
                        response = messageHandler.handle_text_message(message_text)
                        send_message(sender_id, {"type": "text", "content": response})

                    else:
                        send_message(sender_id, {"type": "text", "content": "Sorry, I didn't understand that message."})

    return "EVENT_RECEIVED", 200

# Send message back to Facebook
def send_message(recipient_id, message=None, image_data=None, audio_data=None):
    params = {"access_token": PAGE_ACCESS_TOKEN}

    if image_data:  # Sending an image
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
    elif audio_data:  # Sending audio
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
    elif message:  # Sending text
        headers = {"Content-Type": "application/json"}
        data = {
            "recipient": {"id": recipient_id},
            "message": {"text": message},
        }
        response = requests.post(
            f"https://graph.facebook.com/v21.0/me/messages",
            params=params,
            headers=headers,
            json=data
        )
    else:
        logger.error("No valid data to send.")
        return

    if response.status_code == 200:
        logger.info("Message sent successfully to user %s", recipient_id)
    else:
        try:
            logger.error("Failed to send message: %s", response.json())
        except Exception:
            logger.error("Failed to send message. Status code: %d", response.status_code)

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
    app.run(debug=True, host='0.0.0.0', port=3000)
