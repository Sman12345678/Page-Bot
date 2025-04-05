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
    """Initialize SQLite database"""
    try:
        conn = sqlite3.connect('bot_memory.db', check_same_thread=False)
        c = conn.cursor()
        
        # Create conversations table with support for image analysis and split messages
        c.execute('''CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            message_type TEXT DEFAULT 'text',
            metadata TEXT
        )''')
        
        # Create user_context table with conversation history
        c.execute('''CREATE TABLE IF NOT EXISTS user_context (
            user_id TEXT PRIMARY KEY,
            last_interaction DATETIME,
            conversation_state TEXT,
            conversation_history TEXT
        )''')
        
        conn.commit()
        logger.info("Database initialized successfully")
        return conn
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def split_message(message):
    """Split message if it exceeds Facebook's 2000 character limit"""
    MAX_LENGTH = 2000
    if len(message) <= MAX_LENGTH:
        return [message]
        
    parts = []
    while len(message) > 0:
        if len(message) <= MAX_LENGTH:
            parts.append(message)
            break
            
        # Find the last space within the limit
        split_index = message.rfind(' ', 0, MAX_LENGTH)
        if split_index == -1:
            split_index = MAX_LENGTH
            
        parts.append(message[:split_index])
        message = message[split_index:].lstrip()
    
    # Add part numbers
    return [f"[{i+1}/{len(parts)}] {part}" for i, part in enumerate(parts)]

def store_message(user_id, message, sender, message_type="text"):
    """Store message in database and maintain conversation flow"""
    try:
        c = conn.cursor()
        
        # If it's an image analysis response
        if message_type == "image_analysis":
            # Store the analysis response
            c.execute('''INSERT INTO conversations 
                        (user_id, message, sender, message_type, timestamp)
                        VALUES (?, ?, ?, ?, datetime('now'))''',
                     (user_id, json.dumps(message), "bot", "image_analysis"))
                     
            # Update conversation flow in user_context
            c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', 
                     (user_id,))
            result = c.fetchone()
            history = json.loads(result[0]) if result and result[0] else []
            
            # Add image analysis to conversation history
            history.append({
                "role": "assistant",
                "type": "image_analysis",
                "content": message["analysis"]
            })
            
            # Update user context
            c.execute('''INSERT OR REPLACE INTO user_context 
                        (user_id, conversation_history, last_interaction)
                        VALUES (?, ?, datetime('now'))''',
                     (user_id, json.dumps(history)))
                     
        else:  # Regular text message
            # For split messages, store each part
            if isinstance(message, list):
                for part in message:
                    c.execute('''INSERT INTO conversations 
                                (user_id, message, sender, message_type, timestamp)
                                VALUES (?, ?, ?, ?, datetime('now'))''',
                             (user_id, part, sender, message_type))
                
                # Store in conversation history
                c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', 
                         (user_id,))
                result = c.fetchone()
                history = json.loads(result[0]) if result and result[0] else []
                
                # Add full message to history (combine split parts)
                history.append({
                    "role": "assistant" if sender == "bot" else "user",
                    "content": " ".join(part.split('] ', 1)[1] for part in message)
                })
                
                # Update user context
                c.execute('''INSERT OR REPLACE INTO user_context 
                            (user_id, conversation_history, last_interaction)
                            VALUES (?, ?, datetime('now'))''',
                         (user_id, json.dumps(history)))
            else:
                # Store single message
                c.execute('''INSERT INTO conversations 
                            (user_id, message, sender, message_type, timestamp)
                            VALUES (?, ?, ?, ?, datetime('now'))''',
                         (user_id, message, sender, message_type))
                
                # Update conversation history
                c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''', 
                         (user_id,))
                result = c.fetchone()
                history = json.loads(result[0]) if result and result[0] else []
                
                history.append({
                    "role": "assistant" if sender == "bot" else "user",
                    "content": message
                })
                
                c.execute('''INSERT OR REPLACE INTO user_context 
                            (user_id, conversation_history, last_interaction)
                            VALUES (?, ?, datetime('now'))''',
                         (user_id, json.dumps(history)))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to store message: {str(e)}")

def get_conversation_history(user_id):
    """Get conversation history for a user"""
    try:
        c = conn.cursor()
        c.execute('''SELECT conversation_history FROM user_context WHERE user_id = ?''',
                 (user_id,))
        result = c.fetchone()
        
        if result and result[0]:
            return json.loads(result[0])
        return []
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        return []

def send_message(recipient_id, message):
    """Send message to Facebook Messenger"""
    api_url = f"https://graph.facebook.com/{API_VERSION}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    try:
        # Handle image analysis response
        if isinstance(message, dict) and "type" in message and message["type"] == "image_analysis":
            # Format the analysis message
            analysis_text = f"Image Analysis:\n{message['analysis']}"
            
            # Split if needed and send
            parts = split_message(analysis_text)
            for part in parts:
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": part}
                }
                response = requests.post(api_url, params=params, headers=headers, json=data)
                if response.status_code != 200:
                    return False
            
            # Store in database with conversation flow
            store_message(recipient_id, message, "bot", "image_analysis")
            return True
            
        # Handle regular text messages
        elif isinstance(message, str):
            # Split if needed
            parts = split_message(message)
            
            # Send each part
            for part in parts:
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": part}
                }
                response = requests.post(api_url, params=params, headers=headers, json=data)
                if response.status_code != 200:
                    return False
            
            # Store in database
            store_message(recipient_id, parts if len(parts) > 1 else message, "bot", "text")
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return False

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
                        # Store user message
                        if message_text:
                            store_message(sender_id, message_text, "user")

                        if message_text.startswith(PREFIX):
                            response = messageHandler.handle_command(message_text[len(PREFIX):])
                            send_message(sender_id, response)
                        elif attachments:
                            for attachment in attachments:
                                if attachment["type"] == "image":
                                    response = messageHandler.handle_image(attachment["payload"]["url"])
                                    send_message(sender_id, {
                                        "type": "image_analysis",
                                        "analysis": response
                                    })
                        elif message_text:
                            history = get_conversation_history(sender_id)
                            response = messageHandler.handle_message(message_text, history)
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

@app.route('/status')
def status():
    """Get bot status"""
    uptime = time.time() - start_time
    return jsonify({
        "status": "online",
        "uptime": f"{int(uptime)}s",
        "initialized": INITIALIZED
    })

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
