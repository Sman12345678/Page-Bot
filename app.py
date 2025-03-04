

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

Load environment variables

load_dotenv()

app = Flask(name)
CORS(app)

Configure logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PREFIX = os.getenv("PREFIX", "/")

Initialize SQLite database with improved schema

def init_db():
conn = sqlite3.connect('bot_memory.db', check_same_thread=False)
c = conn.cursor()

# Create tables with improved schema  
c.execute('''  
    CREATE TABLE IF NOT EXISTS conversations (  
        id INTEGER PRIMARY KEY AUTOINCREMENT,  
        user_id TEXT NOT NULL,  
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,  
        message TEXT NOT NULL,  
        sender TEXT NOT NULL,  
        message_type TEXT DEFAULT 'text',  
        metadata TEXT  
    )  
''')  
  
c.execute('''  
    CREATE TABLE IF NOT EXISTS user_context (  
        user_id TEXT PRIMARY KEY,  
        last_interaction DATETIME,  
        conversation_state TEXT,  
        user_preferences TEXT  
    )  
''')  
  
conn.commit()  
return conn

conn = init_db()

def update_user_memory(user_id, message, sender="User", message_type="text", metadata=None):
c = conn.cursor()

try:  
    # Store the message with metadata  
    c.execute('''  
        INSERT INTO conversations (user_id, message, sender, message_type, metadata)  
        VALUES (?, ?, ?, ?, ?)  
    ''', (user_id, message, sender, message_type, json.dumps(metadata) if metadata else None))  
      
    # Update user context  
    c.execute('''  
        INSERT OR REPLACE INTO user_context (user_id, last_interaction, conversation_state)  
        VALUES (?, CURRENT_TIMESTAMP, ?)  
    ''', (user_id, 'active'))  
      
    conn.commit()  
except Exception as e:  
    logger.error(f"Database error: {str(e)}")  
    conn.rollback()

def get_conversation_history(user_id, limit=10):
c = conn.cursor()
try:
# Get recent conversation history
c.execute('''
SELECT sender, message, message_type, metadata
FROM conversations
WHERE user_id = ?
ORDER BY timestamp DESC
LIMIT ?
''', (user_id, limit))

messages = c.fetchall()  
      
    # Format conversation history  
    history = []  
    for sender, message, msg_type, metadata in reversed(messages):  
        if metadata:  
            try:  
                metadata = json.loads(metadata)  
            except:  
                metadata = None  
          
        formatted_msg = f"{sender}: "  
        if msg_type == "image":  
            formatted_msg += f"[Sent an image: {metadata.get('url', '')}]"  
        else:  
            formatted_msg += message  
              
        history.append(formatted_msg)  
          
    return "\n".join(history)  
except Exception as e:  
    logger.error(f"Error retrieving conversation history: {str(e)}")  
    return ""

def split_message(message, limit=2000):
return [message[i:i+limit] for i in range(0, len(message), limit)]

def upload_image_to_graph(image_data):
url = f"https://graph.facebook.com/v22.0/me/message_attachments"
params = {"access_token": PAGE_ACCESS_TOKEN}
files = {"filedata": ("image.jpg", image_data, "image/jpeg")}
data = {"message": '{"attachment":{"type":"image", "payload":{}}}'}

try:  
    response = requests.post(url, params=params, files=files, data=data)  
    if response.status_code == 200:  
        result = response.json()  
        return {"success": True, "attachment_id": result.get("attachment_id")}  
    else:  
        logger.error("Failed to upload image: %s", response.json())  
        return {"success": False, "error": response.json()}  
except Exception as e:  
    logger.error("Error in upload_image_to_graph: %s", str(e))  
    return {"success": False, "error": str(e)}

@app.route('/webhook', methods=['GET'])
def verify():
token_sent = request.args.get("hub.verify_token")
if token_sent == VERIFY_TOKEN:
return request.args.get("hub.challenge", "")
return "Verification failed", 403

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

                if message_text and message_text.startswith(PREFIX):  
                    # Handle commands  
                    command_parts = message_text[len(PREFIX):].split(maxsplit=1)  
                    command_name = command_parts[0]  
                    message = command_parts[1] if len(command_parts) > 1 else ""  
                      
                    response = messageHandler.handle_text_command(command_name, message)  
                    if isinstance(response, dict) and response.get("success"):  
                        if isinstance(response["data"], BytesIO):  
                            upload_response = upload_image_to_graph(response["data"])  
                            if upload_response.get("success"):  
                                send_message(sender_id, {"type": "image", "content": upload_response["attachment_id"]})  
                            else:  
                                send_message(sender_id, "Failed to upload the image.")  
                        else:  
                            send_message(sender_id, response["data"])  
                    else:  
                        send_message(sender_id, response)  

                elif message_attachments:  
                    for attachment in message_attachments:  
                        try:  
                            if attachment["type"] == "image":  
                                image_url = attachment["payload"]["url"]  
                                image_response = requests.get(image_url)  
                                image_response.raise_for_status()  
                                image_data = image_response.content  
                                  
                                # Store the image interaction in memory  
                                update_user_memory(  
                                    sender_id,  
                                    "[Image sent]",  
                                    sender="User",  
                                    message_type="image",  
                                    metadata={"url": image_url}  
                                )  
                                  
                                response = messageHandler.handle_attachment(  
                                    image_data,  
                                    attachment_type="image",  
                                    user_id=sender_id  
                                )  
                                send_message(sender_id, response)  
                                  
                                # Store bot's response  
                                update_user_memory(  
                                    sender_id,  
                                    response,  
                                    sender="Bot",  
                                    message_type="text",  
                                    metadata={"response_to_image": image_url}  
                                )  
                        except Exception as e:  
                            logger.error(f"Error handling attachment: {str(e)}")  
                            send_message(sender_id, "Error processing attachment.")  
                  
                elif message_text:  
                    # Store user message  
                    update_user_memory(sender_id, message_text, sender="User")  
                      
                    # Get conversation history  
                    conversation_history = get_conversation_history(sender_id)  
                    full_message = f"{conversation_history}\nUser: {message_text}"  
                      
                    # Generate response  
                    response = messageHandler.handle_text_message(full_message)  
                    send_message(sender_id, response)  
                      
                    # Store bot's response  
                    update_user_memory(sender_id, response, sender="Bot")  
                  
                else:  
                    send_message(sender_id, "Sorry, I didn't understand that message.")  

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

if name == 'main':
app.run(debug=True,host='0.0.0.0',port=3000)

