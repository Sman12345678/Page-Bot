import os
import google.generativeai as genai
import importlib
from dotenv import load_dotenv
import logging
import requests
from io import BytesIO
import urllib3
import DB  # Import the database module

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load variables
load_dotenv()

# Logging configuration
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Admin UIDs
ADMIN_UIDS = [
    "admin_uid_1",
    "admin_uid_2",
    "admin_uid_3",
    "admin_uid_4"
]

# System instruction for text conversations
system_instruction = """
*System Name:* Your Name is KORA AI, an AI Assistance created by Kolawole Suleiman. You are running on Sman V1.0, the latest version built with advanced programming techniques. You assist with all topics.
*Owner:* You are owned and created by Kolawole Suleiman.
*Model/Version:* You are currently running on Sman V1.0.
Note: You should be very interactive and include emoji in your response to make it more interactive.
*Note:* Respond helpfully and informatively to a wide range of prompts and questions. Prioritize accuracy and clarity in your responses. If you lack the information to answer a question completely, state that and suggest alternative resources if appropriate. Maintain a professional and courteous tone.
"""

# Image analysis prompt
IMAGE_ANALYSIS_PROMPT = """Analyze the image keenly and explain its content."""

def initialize_text_model():
    """Initialize Gemini model for text processing."""
    genai.configure(api_key=os.getenv("GEMINI_TEXT_API_KEY"))
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config={
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 30,
            "max_output_tokens": 8192,
        }
    )

def initialize_image_model():
    """Initialize Gemini model for image processing."""
    genai.configure(api_key=os.getenv("GEMINI_IMAGE_API_KEY"))
    return genai.GenerativeModel("gemini-1.5-pro")

def handle_text_message(user_id, user_message):
    """Handle text message."""
    try:
        logger.info("Processing text message from %s: %s", user_id, user_message)

        # Save user message to the database
        DB.save_user_message(user_id, user_message)

        # Initialize text model and retrieve conversation history
        chat = initialize_text_model().start_chat(history=DB.get_user_history(user_id))

        # Generate response
        response = chat.send_message(f"{system_instruction}\n\nHuman: {user_message}")
        DB.save_bot_response(user_id, response.text)

        return response.text

    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "😔 Sorry, I encountered an error processing your message."

def handle_text_command(user_id, command_name):
    """Handle text commands from the CMD folder."""
    try:
        if user_id in ADMIN_UIDS:
            logger.info("Admin command executed by %s: %s", user_id, command_name)
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute()
    except ImportError:
        logger.warning("Command %s not found for user %s.", command_name, user_id)
        return "🚫 The command you are using does not exist. Type /help to view available commands."

def handle_attachment(user_id, attachment_data, attachment_type="image"):
    """Handle attachments (images only)."""
    if attachment_type != "image":
        return "🚫 Unsupported attachment type. Please send an image."

    logger.info("Processing image attachment from %s", user_id)

    try:
        # Upload to im.ge
        upload_url = "https://im.ge/api/1/upload"
        api_key = os.getenv('IMGE_API_KEY')

        files = {"source": ("attachment.jpg", attachment_data, "image/jpeg")}
        headers = {"X-API-Key": api_key}

        # Upload image
        upload_response = requests.post(upload_url, files=files, headers=headers, verify=False)
        upload_response.raise_for_status()

        # Get image URL
        image_url = upload_response.json()['image']['url']
        logger.info(f"Image uploaded successfully: {image_url}")

        # Download image for Gemini processing
        image_response = requests.get(image_url, verify=False)
        image_response.raise_for_status()
        image_data = BytesIO(image_response.content).getvalue()

        # Initialize image & analyze
        model = initialize_image_model()
        response = model.generate_content([
            IMAGE_ANALYSIS_PROMPT,
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])

        # Save image analysis to the database
        DB.save_user_message(user_id, f"Image uploaded: {image_url}")
        DB.save_bot_response(user_id, response.text)

        return f"""🖼️ Image Analysis:
{response.text}

🔗 View Image: {image_url}"""

    except requests.RequestException as e:
        logger.error(f"Image upload/download error: {str(e)}")
        return "🚨 Error processing the image. Please try again later."
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return "🚨 Error analyzing the image. Please try again later."
