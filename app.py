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
MAX_MESSAGE_LENGTH = 2000  # Maximum message length for Facebook Messenger

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

def split_message(message):
    """Split message into chunks of maximum length"""
    if len(message) <= MAX_MESSAGE_LENGTH:
        return [message]
    
    chunks = []
    current_chunk = ""
    words = message.split()
    
    for word in words:
        if len(current_chunk) + len(word) + 1 <= MAX_MESSAGE_LENGTH:
            current_chunk += " " + word if current_chunk else word
        else:
            chunks.append(current_chunk)
            current_chunk = word
    
    if current_chunk:
        chunks.append(current_chunk)
    
    return chunks

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

def send_message(recipient_id, message):
    """Send message to Facebook Messenger with message splitting"""
    api_url = f"https://graph.facebook.com/{API_VERSION}/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    
    logger.debug(f"=== START SEND MESSAGE ===")
    logger.debug(f"Recipient ID: {recipient_id}")
    logger.debug(f"Message type: {type(message)}")
    
    try:
        if isinstance(message, dict):
            # Handle image messages
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
                response = requests.post(api_url, params=params, headers=headers, json=data)
                if response.status_code != 200:
                    raise Exception(f"Failed to send image: {response.text}")
                return True
        else:
            # Handle text messages with splitting
            if not isinstance(message, str):
                message = str(message)
            
            message_chunks = split_message(message)
            
            for chunk in message_chunks:
                data = {
                    "recipient": {"id": recipient_id},
                    "message": {"text": chunk}
                }
                
                response = requests.post(api_url, params=params, headers=headers, json=data)
                if response.status_code != 200:
                    raise Exception(f"Failed to send message chunk: {response.text}")
                
                # Add a small delay between chunks to prevent rate limiting
                if len(message_chunks) > 1:
                    time.sleep(0.5)
            
            return True

    except Exception as e:
        logger.error(f"Error in send_message: {str(e)}")
        return False
    finally:
        logger.debug("=== END SEND MESSAGE ===")

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
                                        
                                        # Store the user's image message
                                        store_message(sender_id, image_url, "user", "image")
                                        
                                        # Get conversation history
                                        history = get_conversation_history(sender_id)
                                        
                                        # Process image and get analysis
                                        result = messageHandler.handle_attachment(sender_id, image_data, "image")
                                        
                                        # Store bot's analysis
                                        store_message(sender_id, result, "bot", "analysis")
                                        
                                        # Send analysis to user
                                        send_message(sender_id, result)
                                        
                                    except Exception as e:
                                        logger.error(f"Error processing image: {str(e)}")
                                        error_message = "Error processing image"
                                        store_message(sender_id, error_message, "bot", "error")
                                        send_message(sender_id, error_message)
                        elif message_text:
                            # Get conversation history for context
                            history = get_conversation_history(sender_id)
                            response = messageHandler.handle_text_message(sender_id, message_text, history)
                            store_message(sender_id, response, "bot", "text")
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
    uid = request.args.get('uid')  # Get the user ID from the request
    
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        # Use provided uid or generate a default one
        user_id = uid if uid else f"api_user_{str(int(time.time()))}"
        
        # Store the user's message in database
        store_message(user_id, query, "user", "text")
        
        # Get conversation history for context
        history = get_conversation_history(user_id)
        
        # Process the message
        response = messageHandler.handle_text_message(user_id, query, history)
        
        # Store the bot's response in database
        store_message(user_id, response, "bot", "text")
        
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
    logger.info("🎉Application initialized successfully")
except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    raise

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=3000)
