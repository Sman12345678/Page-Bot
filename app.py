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

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Enhanced logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('app_debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger()

# Configuration
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PREFIX = os.getenv("PREFIX", "/")
API_VERSION = "v22.0"
INITIALIZED = False
start_time = time.time()

class FacebookAPIError(Exception):
    """Custom exception for Facebook API errors"""
    pass

def get_current_time():
    """Get current UTC time in YYYY-MM-DD HH:MM:SS format"""
    return datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

def validate_environment():
    """Validate required environment variables and API access"""
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
    """Initialize SQLite database with improved schema"""
    try:
        conn = sqlite3.connect('bot_memory.db', check_same_thread=False)
        c = conn.cursor()
        
        # Create tables
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
    """Store message in database"""
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
            
        history.append({"role": "user" if sender == "user" else "assistant", "content": message})
        
        # Limit history to last 10 messages
        if len(history) > 20:
            history = history[-20:]
            
        c.execute('''INSERT OR REPLACE INTO user_context 
                    (user_id, last_interaction, conversation_history)
                    VALUES (?, ?, ?)''',
                 (user_id, get_current_time(), json.dumps(history)))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to store message: {str(e)}")
def store_image_analysis(user_id, image_url, analysis_result):
    """Store image analysis results in database"""
    try:
        with get_db_cursor() as c:
            current_time = get_current_time()
            # Store the image analysis as a bot message
            c.execute('''INSERT INTO conversations 
                        (user_id, message, sender, message_type, metadata, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)''',
                     (user_id, 
                      analysis_result, 
                      "bot", 
                      "image_analysis",
                      json.dumps({"image_url": image_url}), 
                      current_time))
            
            # Update user context with conversation history
            c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', 
                     (user_id,))
            result = c.fetchone()
            
            history = json.loads(result[0]) if result and result[0] else []
            
            # Add bot's analysis to conversation history
            history.append({
                "role": "assistant",
                "content": analysis_result,
                "type": "image_analysis",
                "timestamp": current_time
            })
            
            # Limit history to last 20 messages
            if len(history) > 20:
                history = history[-20:]
                
            c.execute('''INSERT OR REPLACE INTO user_context 
                        (user_id, last_interaction, conversation_history)
                        VALUES (?, ?, ?)''',
                     (user_id, current_time, json.dumps(history)))
            
    except Exception as e:
        logger.error(f"Failed to store image analysis: {str(e)}")
        raise

def get_conversation_history(user_id):
    """Get conversation history for a user"""
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
    """Log message status to database"""
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

def upload_image_to_graph(image_data):
    """Upload image to Facebook Graph API"""
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

def send_message(recipient_id, message):
    """Send message to Facebook Messenger"""
    api_url = f"https://graph.facebook.com/{API_VERSION}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    logger.debug(f"=== START SEND MESSAGE ===")
    logger.debug(f"Recipient ID: {recipient_id}")
    logger.debug(f"Message type: {type(message)}")
    logger.debug(f"Message content: {message}")

    messages_to_send = []
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
            messages_to_send.append((data, "image", f"[IMAGE: {message['content']}]"))
            logger.debug(f"Prepared image message with attachment_id: {message['content']}")
        else:
            logger.error(f"Unsupported message type: {message.get('type')}")
            return False
    else:
        if not isinstance(message, str):
            message = str(message)

        # Split message into parts if it exceeds 2000 characters
        parts = [message[i:i + 2000] for i in range(0, len(message), 2000)]
        for part in parts:
            data = {
                "recipient": {"id": recipient_id},
                "message": {"text": part}
            }
            messages_to_send.append((data, "text", part))
            logger.debug("Prepared text message")

    success = True
    for data, message_type, message_content in messages_to_send:
        try:
            logger.debug(f"Sending request to Facebook API: {json.dumps(data, indent=2)}")
        
            response = requests.post(api_url, params=params, headers=headers, json=data)
            response_json = response.json() if response.text else {}
            
            logger.debug(f"Facebook API Response Status: {response.status_code}")
            logger.debug(f"Facebook API Response: {json.dumps(response_json, indent=2)}")

            if response.status_code == 200:
                # Store message in database
                store_message(recipient_id, message_content, "bot", message_type)
                
                log_message_status(recipient_id, message_type, "success", metadata=response_json)
                logger.info(f"Successfully sent {message_type} message to {recipient_id}")
            else:
                error_msg = response_json.get("error", {}).get("message", "Unknown error")
                log_message_status(recipient_id, message_type, "failed", error_msg, response_json)
                logger.error(f"Failed to send message: {error_msg}")
                
                # Try to send error message if original message fails
                if message_type == "image":
                    try:
                        error_data = {
                            "recipient": {"id": recipient_id},
                            "message": {"text": f"Failed to send image: {error_msg}"}
                        }
                        requests.post(api_url, params=params, headers=headers, json=error_data)
                    except:
                        pass
                success = False

        except Exception as e:
            error_msg = str(e)
            log_message_status(recipient_id, "error", error_msg)
            logger.error(f"Error in send_message: {error_msg}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            success = False
        finally:
            logger.debug("=== END SEND MESSAGE ===")

    return success

def process_command_response(sender_id, response):
    """Process command response and send appropriate message"""
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
                        logger.debug(f"Sending image message with data: {message_data}")
                        
                        if send_message(sender_id, message_data):
                            logger.info(f"Successfully sent image message to {sender_id}")
                        else:
                            logger.error(f"Failed to send image message to {sender_id}")
                            send_message(sender_id, "Failed to send image")
                    else:
                        error_msg = f"Failed to upload image: {upload_response.get('error')}"
                        logger.error(error_msg)
                        send_message(sender_id, error_msg)
                else:
                    send_message(sender_id, response.get("data", "No data provided"))
            else:
                send_message(sender_id, response.get("data", "Command failed"))
        else:
            send_message(sender_id, str(response))

    except Exception as e:
        logger.error(f"Error processing command response: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        send_message(sender_id, "Error processing command response")
    finally:
        logger.debug("=== END PROCESS COMMAND RESPONSE ===")

def handle_command_message(sender_id, message_text):
    """Handle command messages"""
    command_parts = message_text[len(PREFIX):].split(maxsplit=1)
    command_name = command_parts[0]
    command_args = command_parts[1] if len(command_parts) > 1 else ""

    logger.debug(f"Processing command: {command_name} with args: {command_args}")

    try:
        response = messageHandler.handle_text_command(command_name, command_args)
        
        if isinstance(response, list):
            for item in response:
                process_command_response(sender_id, item)
        else:
            process_command_response(sender_id, response)

    except Exception as e:
        logger.error(f"Error handling command: {str(e)}")
        send_message(sender_id, f"Error processing command: {str(e)}")

@app.route('/webhook', methods=['GET'])
def verify():
    """Verify webhook setup"""
    token_sent = request.args.get("hub.verify_token")
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge", "")
    return "Verification failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook events"""
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
                        # Store user message in database
                        store_message(sender_id, message_text, "user")
                        
                        if message_text.startswith(PREFIX):
                            handle_command_message(sender_id, message_text)
                        elif attachments:
                            for attachment in attachments:
                                if attachment["type"] == "image":
                                    image_url = attachment["payload"]["url"]
                                    try:
                                        response = requests.get(image_url)
                                        image_data = response.content
                                        # Store attachment message
                                        store_message(sender_id, "[IMAGE]", "user", "image")
                                        result = messageHandler.handle_attachment(sender_id, image_data, "image")
                                        send_message(sender_id, result)
                                    except Exception as e:
                                        logger.error(f"Error processing image: {str(e)}")
                                        send_message(sender_id, "Error processing image")
                        elif message_text:
                            # Get conversation history for context
                            history = get_conversation_history(sender_id)
                            response = messageHandler.handle_text_message(sender_id, message_text, history)
                            send_message(sender_id, response)
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        send_message(sender_id, "Sorry, I encountered an error processing your message.")

        return "EVENT_RECEIVED", 200

    except Exception as e:
        logger.error(f"Error in webhook: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return "Internal error", 500

@app.route('/')
def home():
    """Render home page"""
    return render_template('index.html')

@app.route('/api', methods=['GET'])
def api():
    """Handle API requests"""
    query = request.args.get('query')
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Use a fixed user_id for API requests
        api_user_id = "api_user_" + str(int(time.time()))
        response = messageHandler.handle_text_message(api_user_id, query, [])
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get bot status"""
    uptime = get_bot_uptime()
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    return jsonify({
        "status": "online",
        "uptime": f"{int(hours)}h {int(minutes)}m {int(seconds)}s",
        "initialized": INITIALIZED,
        "timestamp": get_current_time()
    })

def get_bot_uptime():
    """Get bot uptime"""
    return time.time() - start_time

# Initialize the application
try:
    validate_environment()
    conn = init_db()
    INITIALIZED = True
    logger.info("Application initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    raise

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
