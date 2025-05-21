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
from datetime import datetime, timezone
from listcmd import register_commands
from intent import classifier 
from CMD import imagine

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()
ADMIN_ID = os.getenv("ADMIN_ID")
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PREFIX = os.getenv("PREFIX", "/")
API_VERSION = "v22.0"
INITIALIZED = False
start_time = time.time()

class FacebookAPIError(Exception):
    pass

def get_current_time():
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def split_long_message(message, max_length=2000):
    if len(message) <= max_length:
        return [message]
    chunks = []
    while message:
        if len(message) <= max_length:
            chunks.append(message)
            break
        split_point = message.rfind(' ', 0, max_length)
        if split_point == -1:
            split_point = max_length
        chunks.append(message[:split_point])
        message = message[split_point:].strip()
    return chunks
def validate_environment():
    if not PAGE_ACCESS_TOKEN:
        raise ValueError("PAGE_ACCESS_TOKEN must be set")
    if not VERIFY_TOKEN:
        raise ValueError("VERIFY_TOKEN must be set")
    try:
        verify_url = f"https://graph.facebook.com/{API_VERSION}/me"
        response = requests.get(verify_url, params={"access_token": PAGE_ACCESS_TOKEN})
        if response.status_code != 200:
            raise FacebookAPIError(f"Invalid PAGE_ACCESS_TOKEN: {response.text}")
        logger.info("Facebook API token validated successfully")
    except Exception as e:
        logger.error(f"Failed to validate Facebook API token: {str(e)}")
        raise

def init_db():
    try:
        conn = sqlite3.connect('bot_memory.db', check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            metadata TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_context (
            user_id TEXT PRIMARY KEY,
            last_interaction DATETIME,
            conversation_state TEXT,
            user_preferences TEXT,
            conversation_history TEXT
        )''')
        c.execute('''CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            sender_id TEXT,
            message_type TEXT,
            status TEXT,
            error_message TEXT,
            metadata TEXT
        )''')
        conn.commit()
        logger.info("Database initialized successfully")
        return conn
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def store_message(user_id, message, sender, message_type="text", metadata=None):
    """
    Store message in database and update conversation history, including all message types.
    Each history item includes 'role', 'content', and 'type'.
    """
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO conversations 
                    (user_id, message, sender, message_type, metadata, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?)''',
                 (user_id, message, sender, message_type, 
                  json.dumps(metadata) if metadata else None, get_current_time()))
        # Update user context with conversation history
        c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', (user_id,))
        result = c.fetchone()
        if result:
            history = json.loads(result[0]) if result[0] else []
        else:
            history = []
        # Standardize role for chat models
        role = "user" if sender == "user" else "assistant"
        history.append({
            "role": role,
            "content": message,
            "type": message_type
        })
        # Limit history to last 50 messages
        if len(history) > 50:
            history = history[-50:]
        c.execute('''INSERT OR REPLACE INTO user_context 
                    (user_id, last_interaction, conversation_history)
                    VALUES (?, ?, ?)''',
                 (user_id, get_current_time(), json.dumps(history)))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to store message: {str(e)}")

def get_conversation_history(user_id):
    """
    Get full conversation history for a user, including all message types.
    """
    try:
        c = conn.cursor()
        c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', (user_id,))
        result = c.fetchone()
        if result and result[0]:
            return json.loads(result[0])
        return []
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        return []

def log_message_status(sender_id, message_type, status, error_message=None, metadata=None):
    try:
        c = conn.cursor()
        c.execute('''INSERT INTO message_logs 
                    (sender_id, message_type, status, error_message, metadata)
                    VALUES (?, ?, ?, ?, ?)''',
                 (sender_id, message_type, status, error_message, 
                  json.dumps(metadata) if metadata else None))
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to log message status: {str(e)}")

def send_message(recipient_id, message):
    """
    Send message to Facebook Messenger. Supports both text and image messages.
    """
    api_url = f"https://graph.facebook.com/{API_VERSION}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    logger.debug(f"=== START SEND MESSAGE ===")
    logger.debug(f"Recipient ID: {recipient_id}")
    logger.debug(f"Message type: {type(message)}")
    logger.debug(f"Message content: {message}")
    try:
        if isinstance(message, dict):
            if message.get("type") == "image":
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {
                        "attachment": {
                            "type": "image",
                            "payload": {
                                "attachment_id": message["content"]
                            }
                        }
                    }
                }
                message_type = "image"
                message_content = f"[IMAGE: {message['content']}]"
                logger.debug(f"Prepared image message with attachment_id: {message['content']}")
                response = requests.post(api_url, params=params, headers=headers, json=data)
                response_json = response.json() if response.text else {}
                if response.status_code == 200:
                    log_message_status(recipient_id, message_type, "success", metadata=response_json)
                    logger.info(f"Successfully sent {message_type} message to {recipient_id}")
                    return True
                else:
                    error_msg = response_json.get("error", {}).get("message", "Unknown error")
                    log_message_status(recipient_id, message_type, "failed", error_msg, response_json)
                    logger.error(f"Failed to send message: {error_msg}")
                    return False
            else:
                logger.error(f"Unsupported message type: {message.get('type')}")
                return False
        else:
            if not isinstance(message, str):
                message = str(message)
            messages = split_long_message(message)
            success = True
            for msg_part in messages:
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": msg_part}
                }
                message_type = "text"
                message_content = msg_part
                logger.debug("Prepared text message")
                logger.debug(f"Sending request to Facebook API: {json.dumps(data, indent=2)}")
                response = requests.post(api_url, params=params, headers=headers, json=data)
                response_json = response.json() if response.text else {}
                logger.debug(f"Facebook API Response Status: {response.status_code}")
                logger.debug(f"Facebook API Response: {json.dumps(response_json, indent=2)}")
                if response.status_code == 200:
                    log_message_status(recipient_id, message_type, "success", metadata=response_json)
                else:
                    error_msg = response_json.get("error", {}).get("message", "Unknown error")
                    log_message_status(recipient_id, message_type, "failed", error_msg, response_json)
                    logger.error(f"Failed to send message: {error_msg}")
                    success = False
                    break
            return success
    except Exception as e:
        error_msg = str(e)
        log_message_status(recipient_id, "error", error_msg)
        logger.error(f"Error in send_message: {error_msg}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    finally:
        logger.debug("=== END SEND MESSAGE ===")

def upload_image_to_graph(image_data):
    url = f"https://graph.facebook.com/{API_VERSION}/me/message_attachments"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    logger.debug("=== START IMAGE UPLOAD ===")
    try:
        if not isinstance(image_data, BytesIO):
            logger.error(f"Invalid image_data type: {type(image_data)}")
            return {"success": False, "error": "Invalid image data type"}
        image_data.seek(0)
        files = {"filedata": ("image.jpg", image_data, "image/jpeg")}
        data = {"message": '{"attachment":{"type":"image", "payload":{}}}'}
        logger.debug("Sending image upload request to Facebook")
        response = requests.post(url, params=params, files=files, data=data)
        response_json = response.json()
        logger.debug(f"Upload response status: {response.status_code}")
        logger.debug(f"Upload response content: {json.dumps(response_json, indent=2)}")
        if response.status_code == 200 and "attachment_id" in response_json:
            logger.info(f"Image upload successful. Attachment ID: {response_json['attachment_id']}")
            return {"success": True, "attachment_id": response_json["attachment_id"]}
        else:
            logger.error(f"Image upload failed. Response: {response.text}")
            return {"success": False, "error": response_json.get("error", {}).get("message", "Unknown error")}
    except Exception as e:
        logger.error(f"Error in upload_image_to_graph: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"success": False, "error": str(e)}
    finally:
        logger.debug("=== END IMAGE UPLOAD ===")

def process_command_response(sender_id, response):
    logger.debug(f"=== START PROCESS COMMAND RESPONSE ===")
    logger.debug(f"Sender ID: {sender_id}")
    logger.debug(f"Response type: {type(response)}")
    logger.debug(f"Response content: {response}")
    try:
        if isinstance(response, dict):
            if response.get("success"):
                if response.get("type") == "image" and isinstance(response.get("data"), BytesIO):
                    logger.debug("Processing image response")
                    upload_response = upload_image_to_graph(response["data"])
                    logger.debug(f"Upload response: {upload_response}")
                    if upload_response.get("success"):
                        message_data = {
                            "type": "image",
                            "content": upload_response["attachment_id"]
                        }
                        # DO NOT store generated image message for commands
                        logger.debug(f"Sending image message with data: {message_data}")
                        send_message(sender_id, message_data)
                    else:
                        error_msg = f"Failed to upload image: {upload_response.get('error')}"
                        logger.error(error_msg)
                        send_message(sender_id, error_msg)
                else:
                    # DO NOT store message
                    send_message(sender_id, response.get("data", "No data provided"))
            else:
                error_msg = response.get("data", "Command failed")
                # DO NOT store message
                send_message(sender_id, error_msg)
        else:
            # DO NOT store message
            send_message(sender_id, str(response))
    except Exception as e:
        logger.error(f"Error processing command response: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_msg = "Error processing command response"
        # DO NOT store message
        send_message(sender_id, error_msg)
    finally:
        logger.debug("=== END PROCESS COMMAND RESPONSE ===")
def handle_command_message(sender_id, message_text):
    command_parts = message_text[len(PREFIX):].split(maxsplit=1)
    command_name = command_parts[0]
    command_args = command_parts[1] if len(command_parts) > 1 else ""
    logger.debug(f"Processing command: {command_name} with args: {command_args}")
    try:
        response = messageHandler.handle_text_command(command_name, command_args,sender_id)
        if isinstance(response, list):
            for item in response:
                process_command_response(sender_id, item)
        else:
            process_command_response(sender_id, response)
    except Exception as e:
        logger.error(f"Error handling command: {str(e)}")
        error_msg = f"Error processing command: {str(e)}"
        
        send_message(sender_id, error_msg)

def report(error_message):
    """
    Send an error message to the bot admin.
    """
    try:
        formatted_message = f"""🚨Error Alert🚨

🔴 Timestamp (UTC): {get_current_time()}

🛠️ **Error Message:**  
{error_message}

📂 |= End of Report =|"""
        send_message(ADMIN_ID, formatted_message)
        logger.info("Error successfully sent to the bot admin.")
    except Exception as e:
        logger.error(f"Failed to notify admin about the error: {e}")

@app.route('/webhook', methods=['GET'])
def verify():
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge", "")
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json()
        logger.debug(f"Received webhook data: {json.dumps(data, indent=2)}")
        if data.get("object") != "page":
            logger.warning("Received non-page object in webhook")
            return "Not a page object", 404
        for entry in data["entry"]:
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event:
                    message = event["message"]
                    message_text = message.get("text", "")
                    attachments = message.get("attachments", [])
                    logger.debug(f"Processing message from {sender_id}: {message_text}")
                    try:
                        # Always store user messages
                        if message_text:
                            store_message(sender_id, message_text, "user", "text")
                        # Handle commands (e.g., /imagine ...)
                        if message_text.startswith(PREFIX):
                            handle_command_message(sender_id, message_text)
                        # Handle image attachments from user
                        elif attachments:
                            for attachment in attachments:
                                if attachment["type"] == "image":
                                    image_url = attachment["payload"]["url"]
                                    try:
                                        response = requests.get(image_url)
                                        image_data = BytesIO(response.content)
                                        # Store user image message
                                        store_message(sender_id, f"[User sent an image: {image_url}]", "user", "image")
                                        # Always pass latest persistent history
                                        history = get_conversation_history(sender_id)
                                        # Process the image and get analysis
                                        result = messageHandler.handle_attachment(sender_id, image_data, "image", history)
                                        # Store bot's analysis result
                                        store_message(sender_id, result, "bot", "analysis")
                                        send_message(sender_id, result)
                                    except Exception as e:
                                        logger.error(f"Error processing image: {str(e)}")
                                        error_msg = "Error processing image"
                                        store_message(sender_id, error_msg, "bot", "error")
                                        send_message(sender_id, error_msg)
                                        report(str(e))
                        # Handle plain text messages
                        elif message_text:
                            history = get_conversation_history(sender_id)
                            intent = classifier.predict_intent(message_text)
                            if intent == "generate_image":
                                response = imagine.execute(message_text, sender_id)
                                if isinstance(response, list):
                                    for item in response:
                                        process_command_response(sender_id, item)
                                else:
                                    process_command_response(sender_id, response)
                                store_message(sender_id, f"[Image generated: {message_text}]", "bot", "image")
                            else:
                                response = messageHandler.handle_text_message(sender_id, message_text, history)
                                store_message(sender_id, response, "bot", "text")
                                send_message(sender_id, response)
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        error_msg = "Sorry, I encountered an error processing your message."
                        store_message(sender_id, error_msg, "bot", "error")
                        send_message(sender_id, error_msg)
                        report(str(e))
        return "EVENT_RECEIVED", 200
    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        #send_message(8711876652167640,e)
        report(str(e))
        return "Internal error", 500

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api():
    query = request.args.get('query')
    uid = request.args.get('uid')
    if not query:
        return jsonify({"error": "No query provided"}), 400
    try:
        user_id = uid if uid else f"api_user_{str(int(time.time()))}"
        store_message(user_id, query, "user", "text")
        history = get_conversation_history(user_id)
        response = messageHandler.handle_text_message(user_id, query, history)
        store_message(user_id, response, "bot", "text")
        return jsonify({"response":response})
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    uptime = get_bot_uptime()
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    return jsonify({
        "status": "online",
        "uptime": f"{int(hours)}h {int(minutes)}m {int(seconds)}s",
        "initialized": INITIALIZED,
        "timestamp": get_current_time()
    })

@app.route('/history', methods=['GET'])
def user_history():
    user_id = request.args.get("id")
    admin_code = request.args.get("admin")
    # Replace 'your_secret_admin_code' with your actual admin code or use an environment variable
    if not user_id:
        return jsonify({"error": "No user id provided"}), 400
    if admin_code != os.getenv("ADMIN_CODE", "ICU14CU"):
        return jsonify({"error": "Invalid admin code"}), 403
    try:
        history = get_conversation_history(user_id)
        return jsonify({"user_id": user_id, "conversation_history": history})
    except Exception as e:
        logger.error(f"Error fetching conversation history: {str(e)}")
        return jsonify({"error": str(e)}), 500

def get_bot_uptime():
    return time.time() - start_time

try:
    validate_environment()
    conn = init_db()
    INITIALIZED = True
    logger.info("🎉Application initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    raise

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=3000)
    register_commands()
