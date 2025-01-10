import os
import google.generativeai as genai
import importlib
from dotenv import load_dotenv
import logging
import requests
from io import BytesIO
import urllib3
import time
from app import app  # Import the Flask app instance
from Brain import google_search  # Import the function you want to call

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
load_dotenv()

# Logging setup
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def run_google_search():
    with app.app_context():  # Set up the Flask application context
        result = google_search()  # This should rely on `g.message_text` set in app.py
        return f"{result}"

if __name__ == "__main__":
    # Get the result of google_search
    Answer = run_google_search()
    
    # Get the current time
    time_now = time.asctime(time.localtime(time.time()))
    
    # Format the system instruction with the result
    system_instruction = """
    *System Name:* Your Name is KORA AI, an AI Assistance created by Kolawole Suleiman. 
    You are running on Sman V1.0, the latest version built with high programming techniques. 
    You should assist with all topics.

    *Owner:* You are owned and created by Kolawole Suleiman.
    *Model/Version:* You are currently running on Sman V1.0.
    *Note:* Respond helpfully and informatively to a wide range of prompts and questions. 
    Prioritize accuracy and clarity in your responses. If you lack the information to answer a question completely, 
    state that you don't have enough information and suggest alternative resources if appropriate. 
    Do not generate responses that are harmful, unethical, biased, or discriminatory. 
    Maintain a professional and courteous tone in all interactions.

    Today date is: {}
    Search result: {}
    """.format(time_now, Answer)
    
    


# Image analysis prompt
IMAGE_ANALYSIS_PROMPT = """Analyize the image keenly and explain it's content,if it's a text translate it and say the language used"""

def initialize_text_model():
    """Initialize Gemini model for text processing"""
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
    """Initialize Gemini model for image processing"""
    genai.configure(api_key=os.getenv("GEMINI_IMAGE_API_KEY"))
    return genai.GenerativeModel("gemini-1.5-pro")

def handle_text_message(user_message):
    
    try:
        logger.info("Processing text message: %s", user_message)
        
        # Initialize text model and start chat
        chat = initialize_text_model().start_chat(history=[])
        
        # Generate response
        response = chat.send_message(f"{system_instruction}\n\nHuman: {user_message}")
        return response.text

    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "😔 Sorry, I encountered an error processing your message."

def handle_text_command(command_name,message):
    """Handle text commands from CMD folder"""
    try:
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute(message)
    except ImportError:
        logger.warning("Command %s not found.", command_name)
        return "🚫 The Command you are using does not exist, Type /help to view Available Command"

def handle_attachment(attachment_data, attachment_type="image"):
    
    if attachment_type != "image":
        return "🚫 Unsupported attachment type. Please send an image."

    logger.info("Processing image attachment")
    
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

        return f"""🖼️ Image Analysis:
{response.text}

🔗 View Image: {image_url}"""

    except requests.RequestException as e:
        logger.error(f"Image upload/download error: {str(e)}")
        return "🚨 Error processing the image. Please try again later."
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        return "🚨 Error analyzing the image. Please try again later."
