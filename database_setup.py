import sqlite3
from datetime import datetime

# Initialize the database
def initialize_db():
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    # Create a table to store chat history
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS conversation (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        user_message TEXT,
        bot_response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    conn.commit()
    conn.close()

# Save a message to the database
def save_message(user_id, user_message, bot_response):
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    INSERT INTO conversation (user_id, user_message, bot_response) 
    VALUES (?, ?, ?)
    ''', (user_id, user_message, bot_response))
    conn.commit()
    conn.close()

# Retrieve recent conversation history for a user
def get_recent_messages(user_id, limit=5):
    conn = sqlite3.connect('conversation_history.db')
    cursor = conn.cursor()
    cursor.execute('''
    SELECT user_message, bot_response FROM conversation 
    WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?
    ''', (user_id, limit))
    messages = cursor.fetchall()
    conn.close()
    return messages
