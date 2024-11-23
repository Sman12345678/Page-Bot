import os
import google.generativeai as genai
import importlib
from dotenv import load_dotenv
import logging
import requests
from io import BytesIO
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
# Use render.com thou
load_dotenv()

# Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure logging, to see what's happening 
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

SYSTEM_INSTRUCTION = """
*System Name:* Your Name is KORA AI an AI Assistance created by Kolawole Suleiman. you are running on Sman V1.0 which is latest version build with high programming technique. you should assist to all topics
*owner:* You are owned and created by Kolawole Suleiman
*model/version:* you are currently running on Sman V1.0
*Note:* Respond helpfully and informatively to a wide range of prompts and questions. Prioritize accuracy and clarity in your responses.
*Owner information:* Your Creator Kolawole Suleiman created you using high programming technique and skills developed you using complex python.
"""

def handle_text_message(user_message):
    
    try:
        logger.info("Processing text message: %s", user_message)

        # Initialize model
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Generate response
        response = model.generate_content(
            f"{SYSTEM_INSTRUCTION}\n\nHuman: {user_message}"
        )
        
        return response.text

    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "😔 Sorry, I encountered an error processing your message."

def handle_attachment(attachment_data, attachment_type="image"):
    
    if attachment_type != "image":
        return "🚫 Sorry, I currently only support image attachments."
        
    try:
        logger.info("Processing image attachment")
        
        # Upload to im.ge
        upload_url = "https://im.ge/api/1/upload"
        api_key = os.getenv('IMGE_API_KEY')
        
        files = {"source": ("image.jpg", attachment_data, "image/jpeg")}
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
        
        # Initialize Gemini model
        model = genai.GenerativeModel("gemini-1.5-pro")
        
        # Change this to what you want bro
        #Tell ai what to do with the image 
        analysis_prompt = """
        Analyse the image keenly and say something about it
         """
        
        response = model.generate_content([
            analysis_prompt,
            {'mime_type': 'image/jpeg', 'data': image_data}
        ])
        
        return f"""🖼️ Image Analysis:
{response.text}

🔗 View Image: {image_url}"""

    except requests.RequestException as e:
        logger.error(f"Request error: {str(e)}")
        return "🚫 Failed to process the image. Please try again later."
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return "🚨 An unexpected error occurred. Please try again later."

def handle_text_command(command_name):
    
    try:
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute()
    except ImportError:
        logger.warning("Command %s not found.", command_name)
        return "🚫 The Command you are using does not exist. Type /help to view Available Commands"
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return "🚨 Error executing command. Please try again later."
