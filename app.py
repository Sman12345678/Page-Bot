import os
import logging
import sqlite3
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from flask_cors import CORS
import requests
import messageHandler
import time
from io import BytesIO
import json
import traceback

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,  # Changed to DEBUG for more detailed logs
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PREFIX = os.getenv("PREFIX", "/")

# Initialize SQLite database with improved schema
def init_db():
    conn = sqlite3.connect('bot_memory.db', check_same_thread=False)
    c = conn.cursor()
    # ... [rest of init_db remains the same]
    return conn

conn = init_db()

def upload_image_to_graph(image_data):
    """Enhanced image upload function with detailed logging"""
    url = f"https://graph.facebook.com/v22.0/me/message_attachments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    logger.debug(f"Preparing to upload image to Facebook Graph API")
    logger.debug(f"Image data type: {type(image_data)}")
    
    try:
        if isinstance(image_data, BytesIO):
            image_data.seek(0)  # Reset pointer to start of file
            files = {"filedata": ("image.jpg", image_data, "image/jpeg")}
        else:
            logger.error(f"Invalid image_data type: {type(image_data)}")
            return {"success": False, "error": "Invalid image data type"}

        data = {"message": '{"attachment":{"type":"image", "payload":{}}}'}
        
        logger.debug("Sending request to Facebook Graph API")
        response = requests.post(url, params=params, files=files, data=data)
        logger.debug(f"Facebook Graph API Response Status: {response.status_code}")
        logger.debug(f"Facebook Graph API Response Content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            logger.info(f"Successfully uploaded image, got attachment_id: {result.get('attachment_id')}")
            return {"success": True, "attachment_id": result.get("attachment_id")}
        else:
            logger.error(f"Failed to upload image. Status: {response.status_code}, Response: {response.text}")
            return {"success": False, "error": response.text}
    except Exception as e:
        logger.error(f"Error in upload_image_to_graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}

def send_message(recipient_id, message):
    """Enhanced message sending function with detailed logging"""
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    logger.debug(f"Preparing to send message to recipient {recipient_id}")
    logger.debug(f"Message type: {type(message)}")
    logger.debug(f"Message content: {message}")

    try:
        if isinstance(message, dict):
            message_type = message.get("type")
            content = message.get("content")
            
            logger.debug(f"Processing structured message of type: {message_type}")
            
            if message_type == "image":
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {
                        "attachment": {
                            "type": "image",
                            "payload": {"attachment_id": content}
                        }
                    }
                }
                logger.debug(f"Prepared image message with attachment_id: {content}")
            else:
                logger.error(f"Unsupported message type: {message_type}")
                return
        else:
            if not isinstance(message, str):
                message = str(message)
            
            messages = split_message(message)
            for msg in messages:
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": msg}
                }
                
                logger.debug(f"Sending text message: {msg[:100]}...")
                
                try:
                    response = requests.post(
                        "https://graph.facebook.com/v22.0/me/messages",
                        params=params,
                        headers=headers,
                        json=data
                    )
                    
                    logger.debug(f"Facebook API Response Status: {response.status_code}")
                    logger.debug(f"Facebook API Response Content: {response.text}")
                    
                    if response.status_code != 200:
                        logger.error(f"Failed to send message: {response.text}")
                        
                except Exception as e:
                    logger.error(f"Error sending message part: {str(e)}")
                    logger.error(f"Traceback: {traceback.format_exc()}")
            return

        # Send the message
        response = requests.post(
            "https://graph.facebook.com/v22.0/me/messages",
            params=params,
            headers=headers,
            json=data
        )
        
        logger.debug(f"Facebook API Response Status: {response.status_code}")
        logger.debug(f"Facebook API Response Content: {response.text}")
        
        if response.status_code != 200:
            logger.error(f"Failed to send message: {response.text}")
            
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    logger.info("Received webhook data: %s", json.dumps(data, indent=2))

    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                if "message" in event:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"].get("text")
                    message_attachments = event["message"].get("attachments")

                    logger.debug(f"Processing message from sender {sender_id}")
                    logger.debug(f"Message text: {message_text}")
                    logger.debug(f"Message attachments: {message_attachments}")

                    if isinstance(message_text, bytes):
                        try:
                            logger.debug("Processing byte message as image")
                            image_data = BytesIO(message_text)
                            upload_response = upload_image_to_graph(image_data)
                            logger.debug(f"Upload response: {upload_response}")
                            
                            if upload_response.get("success"):
                                attachment_id = upload_response["attachment_id"]
                                send_message(sender_id, {"type": "image", "content": attachment_id})
                            else:
                                send_message(sender_id, "Failed to upload the image.")
                        except Exception as e:
                            logger.error(f"Error handling byte message: {str(e)}")
                            logger.error(f"Traceback: {traceback.format_exc()}")
                            send_message(sender_id, "Error processing byte message.")
                        return "EVENT_RECEIVED", 200

                    if message_text and message_text.startswith(PREFIX):
                        logger.debug(f"Processing command message: {message_text}")
                        command_parts = message_text[len(PREFIX):].split(maxsplit=1)
                        command_name = command_parts[0]
                        message = command_parts[1] if len(command_parts) > 1 else ""

                        logger.debug(f"Command name: {command_name}")
                        logger.debug(f"Command message: {message}")

                        response = messageHandler.handle_text_command(command_name, message)
                        logger.debug(f"Command response type: {type(response)}")
                        logger.debug(f"Command response content: {response}")

                        if isinstance(response, list):
                            logger.debug(f"Processing list response with {len(response)} items")
                            for res in response:
                                logger.debug(f"Processing response item: {res}")
                                if isinstance(res, dict):
                                    logger.debug(f"Response item keys: {res.keys()}")
                                    logger.debug(f"Response item success: {res.get('success')}")
                                    logger.debug(f"Response item type: {res.get('type')}")
                                    
                                    if res.get("success") and res.get("type") == "image" and isinstance(res.get("data"), BytesIO):
                                        logger.debug("Processing image response")
                                        upload_response = upload_image_to_graph(res["data"])
                                        logger.debug(f"Upload response: {upload_response}")
                                        
                                        if upload_response.get("success"):
                                            send_message(sender_id, {
                                                "type": "image",
                                                "content": upload_response["attachment_id"]
                                            })
                                        else:
                                            send_message(sender_id, "Failed to upload the image.")
                                    else:
                                        send_message(sender_id, res.get("data", "Unknown response"))
                        elif isinstance(response, dict) and response.get("success"):
                            logger.debug("Processing single dict response")
                            if isinstance(response.get("data"), BytesIO):
                                upload_response = upload_image_to_graph(response["data"])
                                logger.debug(f"Upload response: {upload_response}")
                                
                                if upload_response.get("success"):
                                    send_message(sender_id, {
                                        "type": "image",
                                        "content": upload_response["attachment_id"]
                                    })
                                else:
                                    send_message(sender_id, "Failed to upload the image.")
                            else:
                                send_message(sender_id, response["data"])
                        else:
                            logger.debug("Processing simple response")
                            send_message(sender_id, response)

    return "EVENT_RECEIVED", 200
def send_message(recipient_id, message):
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}

    if isinstance(message, dict):  
        message_type = message.get("type")  
        content = message.get("content")  
        
        if message_type == "image":  
            data = {  
                "recipient": {"id": recipient_id},  
                "message": {  
                    "attachment": {  
                        "type": "image",  
                        "payload": {"attachment_id": content}  
                    }  
                }  
            }  
        else:  
            logger.error(f"Unsupported message type: {message_type}")  
            return  
    else:  
        if not isinstance(message, str):  
            message = str(message)  
        
        messages = split_message(message)  
        for msg in messages:  
            data = {  
                "recipient": {"id": recipient_id},  
                "message": {"text": msg}  
            }  
            
            try:  
                response = requests.post(  
                    "https://graph.facebook.com/v22.0/me/messages",  
                    params=params,  
                    headers=headers,  
                    json=data  
                )  
                
                if response.status_code != 200:  
                    logger.error(f"Failed to send message: {response.text}")  
            except Exception as e:  
                logger.error(f"Error sending message: {str(e)}")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api():
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    response = messageHandler.handle_text_message(query)  
    return jsonify({"response": response})

start_time = time.time()


# Expose the start_time so CMD can access it
def get_bot_uptime():
    return time.time() - start_time


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
