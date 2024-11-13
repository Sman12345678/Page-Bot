import os
import google.generativeai as genai
import importlib
from dotenv import load_dotenv
import logging
from database_setup import initialize_db, save_message, get_recent_messages

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize the database
initialize_db()

system_instruction = """
*System Name:*Your Name is KORA AI, an AI Assistant created by Kolawole Suleiman. You are running on Sman V1.0, the latest version built with advanced programming techniques. You should assist with all topics.
*owner/creator:*You were created and owned by Kolawole Suleiman
*Version:*You are running on Sman V1.0
"""

# Handle general text messages
def handle_text_message(user_id, user_message):
    """
    Processes regular text messages from the user.
    
    :param user_id: Unique identifier for the user
    :param user_message: The message text from the user.
    :return: AI-generated response.
    """
    try:
        # Retrieve recent chat history for context
        recent_history = get_recent_messages(user_id)
        history_context = "\n".join([f"Human: {msg[0]}\nKora AI: {msg[1]}" for msg in recent_history])

        logger.info("Processing text message: %s", user_message)

        # Start a chat with the model
        chat = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={
                "temperature": 0.3,
                "top_p": 0.95,
                "top_k": 64,
                "max_output_tokens": 8192,
            }
        ).start_chat(history=[])

        # Include recent chat history for context
        response = chat.send_message(f"{system_instruction}\n\n{history_context}\n\nHuman: {user_message}")
        
        # Save the conversation in the database
        save_message(user_id, user_message, response.text)

        return response.text

    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "Sorry, I encountered an error processing your message."

# Handle attachments (e.g., direct images)
def handle_attachment(user_id, attachment_data, attachment_type="image"):
    """
    Processes attachments sent by the user.
    
    :param user_id: Unique identifier for the user
    :param attachment_data: Raw data of the attachment (e.g., image bytes).
    :param attachment_type: Type of the attachment (default is 'image').
    :return: AI-generated response or a message about the attachment.
    """
    if attachment_type == "image":
        logger.info("Direct image received for processing.")
        
        # Placeholder to check if model supports image processing
        image_supported = False  # Change to True if model supports direct image processing
        
        if image_supported:
            try:
                chat = genai.GenerativeModel(
                    model_name="gemini-1.5-flash",
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.95,
                        "top_k": 64,
                        "max_output_tokens": 8192,
                    }
                ).start_chat(history=[])
                response = chat.send_message(f"{system_instruction}\n\nAnalyze this image")
                
                # Save response in conversation history
                save_message(user_id, "Sent an image", response.text)
                return response.text

            except Exception as e:
                logger.error("Failed to process image: %s", str(e))
                return "Error processing the image."
        else:
            return "Image processing is not supported in this version of the assistant."
    
    logger.info("Unsupported attachment type: %s", attachment_type)
    return "Unsupported attachment type."

# Handle text commands
def handle_text_command(command_name):
    try:
        # Dynamically import command from CMD folder
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute()
    except ImportError:
        logger.warning("Command %s not found.", command_name)
        return "Command not found."
