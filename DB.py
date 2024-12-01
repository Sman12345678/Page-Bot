import sqlite3
import time
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Database file
DB_FILE = "bot_data.db"

# Initialize the database
def initialize_database():
    """Create the necessary tables if they don't exist."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        # Create table for storing user messages and bot responses
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)

        # Create table for storing admin activity logs (optional)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS admin_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_id TEXT NOT NULL,
                activity TEXT NOT NULL,
                timestamp INTEGER NOT NULL
            )
        """)

        conn.commit()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error("Error initializing database: %s", str(e))
    finally:
        conn.close()

def save_user_message(user_id, message):
    """Save user message to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO conversation (user_id, message, timestamp)
            VALUES (?, ?, ?)
        """, (user_id, message, timestamp))

        conn.commit()
        logger.info("Saved user message: %s", message)
    except Exception as e:
        logger.error("Error saving user message: %s", str(e))
    finally:
        conn.close()

def save_bot_response(user_id, response):
    """Save bot response to the database."""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO conversation (user_id, message, timestamp)
            VALUES (?, ?, ?)
        """, (user_id, response, timestamp))

        conn.commit()
        logger.info("Saved bot response: %s", response)
    except Exception as e:
        logger.error("Error saving bot response: %s", str(e))
    finally:
        conn.close()

def get_user_history(user_id, time_limit=86400):
    """
    Retrieve conversation history for a user within the last 24 hours.
    :param user_id: The user's unique identifier.
    :param time_limit: Time limit for history in seconds (default: 24 hours).
    :return: List of messages as a conversation history.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        current_time = int(time.time())
        time_threshold = current_time - time_limit

        cursor.execute("""
            SELECT message FROM conversation
            WHERE user_id = ? AND timestamp >= ?
            ORDER BY timestamp ASC
        """, (user_id, time_threshold))

        messages = [row[0] for row in cursor.fetchall()]
        logger.info("Retrieved user history for %s", user_id)

        return messages
    except Exception as e:
        logger.error("Error retrieving user history: %s", str(e))
        return []
    finally:
        conn.close()

def clear_old_conversations(time_limit=86400):
    """
    Delete conversations older than the specified time limit (default: 24 hours).
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
        logger.info("Old conversations cleared.")
    except Exception as e:
        logger.error("Error clearing old conversations: %s", str(e))
    finally:
        conn.close()

def log_admin_activity(admin_id, activity):
    """
    Log admin activities in the database.
    :param admin_id: The admin's unique identifier.
    :param activity: Description of the activity.
    """
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()

        timestamp = int(time.time())
        cursor.execute("""
            INSERT INTO admin_logs (admin_id, activity, timestamp)
            VALUES (?, ?, ?)
        """, (admin_id, activity, timestamp))

        conn.commit()
        logger.info("Logged admin activity for %s: %s", admin_id, activity)
    except Exception as e:
        logger.error("Error logging admin activity: %s", str(e))
    finally:
        conn.close()

# Initialize the database on import
initialize_database()
