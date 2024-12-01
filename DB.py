import sqlite3
import time
import logging

# Database file path
DB_FILE = "bot_database.db"

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def initialize_database():
    """
    Initialize the database and create necessary tables if they do not exist.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create conversation table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                role TEXT CHECK(role IN ('user', 'model')) NOT NULL,
                message TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)
        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error("Error initializing database: %s", str(e))
    finally:
        conn.close()

def save_message(user_id, role, message):
    """
    Save a message in the database with its role and timestamp.
    :param user_id: The user's unique identifier.
    :param role: The role of the message sender ('user' or 'model').
    :param message: The content of the message.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO conversation (user_id, role, message, timestamp)
            VALUES (?, ?, ?, ?)
        """, (user_id, role, message, timestamp))
        conn.commit()
        logger.info("Message saved successfully for user %s.", user_id)
    except Exception as e:
        logger.error("Error saving message for user %s: %s", user_id, str(e))
    finally:
        conn.close()

def get_user_history(user_id, time_limit=86400):
    """
    Retrieve conversation history for a user within the last 24 hours.
    :param user_id: The user's unique identifier.
    :param time_limit: Time limit for history in seconds (default: 24 hours).
    :return: List of messages as a conversation history in the format required by the Gemini API.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        current_time = int(time.time())
        time_threshold = current_time - time_limit

        # Fetch messages with roles from the database
        cursor.execute("""
            SELECT role, message FROM conversation
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (user_id, time_threshold))

        # Format the results for the Gemini API
        messages = [{"role": row[0], "content": row[1]} for row in cursor.fetchall()]
        logger.info("Retrieved user history for %s.", user_id)

        return messages
    except Exception as e:
        logger.error("Error retrieving user history for %s: %s", user_id, str(e))
        return []
    finally:
        conn.close()

def clear_old_messages(time_limit=86400):
    """
    Delete messages older than the specified time limit (default: 24 hours).
    :param time_limit: Time limit for message retention in seconds.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        current_time = int(time.time())
        time_threshold = current_time - time_limit

        cursor.execute("""
            DELETE FROM conversation WHERE timestamp < ?
        """, (time_threshold,))
        conn.commit()
        logger.info("Old messages cleared successfully.")
    except Exception as e:
        logger.error("Error clearing old messages: %s", str(e))
    finally:
        conn.close()

# Initialize the database when this file is imported
initialize_database()
