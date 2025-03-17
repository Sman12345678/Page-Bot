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
        
        # Create tables with improved schema
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_type TEXT NOT NULL,
            metadata TEXT,
            is_bot_response BOOLEAN DEFAULT 0
        )''')
        
        c.execute('''CREATE INDEX IF NOT EXISTS idx_conversations_user_time 
                    ON conversations(user_id, timestamp DESC)''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        return conn
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def store_message(user_id, message, sender, message_type="text", metadata=None, is_bot_response=False):
    """Store a message in the database and maintain 10 message limit"""
    try:
        c = conn.cursor()
        
        # Insert new message
        c.execute('''INSERT INTO conversations 
                    (user_id, message, sender, message_type, metadata, timestamp, is_bot_response)
                    VALUES (?, ?, ?, ?, ?, datetime('now'), ?)''',
                    (user_id, message, sender, message_type, 
                     json.dumps(metadata) if metadata else None, is_bot_response))
        
        # Keep only latest 10 messages per user
        c.execute('''DELETE FROM conversations 
                    WHERE id NOT IN (
                        SELECT id FROM (
                            SELECT id FROM conversations 
                            WHERE user_id = ? 
                            ORDER BY timestamp DESC 
                            LIMIT 10
                        )
                    ) AND user_id = ?''', (user_id, user_id))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to store message: {str(e)}")
        conn.rollback()
        return False

def get_conversation_history(user_id, limit=10):
    """Get conversation history for a user"""
    try:
        c = conn.cursor()
        c.execute('''SELECT timestamp, message, sender, message_type, metadata, is_bot_response 
                    FROM conversations 
                    WHERE user_id = ? 
                    ORDER BY timestamp DESC 
                    LIMIT ?''', (user_id, limit))
        return c.fetchall()
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        return []

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
                        # Store bot's image response
                        store_message(sender_id, "Image Response", "bot", "image", 
                                    {"attachment_id": upload_response["attachment_id"]}, True)
                        
                        logger.debug(f"Sending image message with data: {message_data}")
                        if send_message(sender_id, message_data):
                            logger.info(f"Successfully sent image message to {sender_id}")
                        else:
                            error_msg = "Failed to send image"
                            store_message(sender_id, error_msg, "bot", "text", None, True)
                            send_message(sender_id, error_msg)
                    else:
                        error_msg = f"Failed to upload image: {upload_response.get('error')}"
                        store_message(sender_id, error_msg, "bot", "text", None, True)
                        send_message(sender_id, error_msg)
                else:
                    response_text = response.get("data", "No data provided")
                    store_message(sender_id, response_text, "bot", "text", None, True)
                    send_message(sender_id, response_text)
            else:
                error_msg = response.get("data", "Command failed")
                store_message(sender_id, error_msg, "bot", "text", None, True)
                send_message(sender_id, error_msg)
        else:
            store_message(sender_id, str(response), "bot", "text", None, True)
            send_message(sender_id, str(response))

    except Exception as e:
        logger.error(f"Error processing command response: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        error_msg = "Error processing command response"
        store_message(sender_id, error_msg, "bot", "text", None, True)
        send_message(sender_id, error_msg)
    finally:
        logger.debug("=== END PROCESS COMMAND RESPONSE ===")

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
                        if message_text.startswith(PREFIX):
                            # Store user's command
                            store_message(sender_id, message_text, "user", "command")
                            handle_command_message(sender_id, message_text)
                        elif attachments:
                            for attachment in attachments:
                                if attachment["type"] == "image":
                                    # Store user's image message
                                    store_message(sender_id, "Image Sent", "user", "image", 
                                                {"url": attachment["payload"]["url"]})
                                    
                                    image_url = attachment["payload"]["url"]
                                    try:
                                        response = requests.get(image_url)
                                        image_data = response.content
                                        result = messageHandler.handle_attachment(image_data, "image")
                                        # Store bot's analysis response
                                        store_message(sender_id, str(result), "bot", "image_analysis", None, True)
                                        send_message(sender_id, result)
                                    except Exception as e:
                                        logger.error(f"Error processing image: {str(e)}")
                                        error_msg = "Error processing image"
                                        store_message(sender_id, error_msg, "bot", "error", None, True)
                                        send_message(sender_id, error_msg)
                        elif message_text:
                            # Store user's message
                            store_message(sender_id, message_text, "user", "text")
                            response = messageHandler.handle_text_message(message_text)
                            # Store bot's response
                            store_message(sender_id, str(response), "bot", "text", None, True)
                            send_message(sender_id, response)
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
                        error_msg = "Sorry, I encountered an error processing your message."
                        store_message(sender_id, error_msg, "bot", "error", None, True)
                        send_message(sender_id, error_msg)

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
        response = messageHandler.handle_text_message(query)
        return jsonify({"response": response})
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
    app.run(debug=True, host='0.0.0.0',port=3000)
