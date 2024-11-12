import os
import google.generativeai as genai
import importlib
from dotenv import load_dotenv
import logging
from io import BytesIO

# Load environment variables
load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

system_instruction = """
*System Name:*Your Name is KORA AI Assistance by Kolawole Suleiman...
"""

# Handle general text messages
def handle_text_message(user_message):
    """
    Processes regular text messages from the user.
    
    :param user_message: The message text from the user.
    :return: AI-generated response.
    """
    try:
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

        # Generate a response to the user's message
        response = chat.send_message(f"{system_instruction}\n\nHuman: {user_message}")
        return response.text

    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "Sorry, I encountered an error processing your message."

# Handle text commands
def handle_text_command(command_name):
    try:
        # Dynamically import command from CMD folder
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute()
    except ImportError:
        logger.warning("Command %s not found.", command_name)
        return "Command not found."

# Handle attachments (e.g., direct images)
def handle_attachment(attachment_data, attachment_type="image"):
    """
    Processes attachments sent by the user.
    
    :param attachment_data: Raw data of the attachment (e.g., image bytes).
    :param attachment_type: Type of the attachment (default is 'image').
    :return: AI-generated response or a message about the attachment.
    """
    if attachment_type == "image":
        logger.info("Direct image received for processing.")
        
        try:
            # Send image data for processing (if supported by model)
            chat = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                }
            ).start_chat(history=[])

            # Generate response for the image (modify if direct image processing is supported)
            response = chat.send_message(f"{system_instruction}\n\nAnalyze this image.",attachment_data)
            logger.info("Image processed successfully.")
            return response.text

        except Exception as e:
            logger.error("Failed to process image: %s", str(e))
            return "Error processing the image."
    
    logger.info("Unsupported attachment type: %s", attachment_type)
    return "Unsupported attachment type."
