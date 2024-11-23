import os
import google.generativeai as genai
import importlib
from dotenv import load_dotenv
import logging
import requests
from PIL import Image
from io import BytesIO

# Load environment variables but try using render.com 
# although i think you're already doing that 
load_dotenv()

#  Google Generative AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Configure logging, this is very important bro
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

#  instructions
SYSTEM_INSTRUCTION = """
*System Name:* Your Name is KORA AI an AI Assistance created by Kolawole Suleiman. you are running on Sman V1.0 which is latest version build with high programming technique. you should assist to all topics
*owner:* You are owned and created by Kolawole Suleiman
*model/version:* you are currently running on Sman V1.0
*Note:* Respond helpfully and informatively to a wide range of prompts and questions. Prioritize accuracy and clarity in your responses. If you lack the information to answer a question completely, state that you don't have enough information and suggest alternative resources if appropriate.
*Owner information:* Your Creator Kolawole Suleiman created you using high programming technique and skills developed you using complex python and he can be contacted via Facebook on "https://www.facebook.com/profile.php?id=61553565805276"
"""

def get_gemini_model(model_name="gemini-1.5-flash"):
    """
    Initialize and return a Gemini model instance with specified configuration.
    """
    return genai.GenerativeModel(
        model_name=model_name,
        generation_config={
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
        }
    )

def handle_text_message(user_message):
    """
    Process text messages using Gemini API.
    
    Args:
        user_message (str): The message text from the user
    Returns:
        str: AI-generated response
    """
    try:
        logger.info("Processing text message: %s", user_message)
        
        # Initialize chat with the model
        chat = get_gemini_model().start_chat(history=[])
        
        # Combine system instruction with user message 
         # 🛑 I don't recommend but for now
        full_prompt = f"{SYSTEM_INSTRUCTION}\n\nHuman: {user_message}"
        
        # Generate response
        response = chat.send_message(full_prompt)
        logger.info("Generated response successfully")
        
        return response.text

    except Exception as e:
        logger.error("Error processing text message: %s", str(e))
        return "😔 I encountered an error processing your message. Please try again later."

def upload_image_to_imge(image_data):
    """
    ######## Getting to image🗿 ########
    Upload image to im.ge and return the direct link.
    
    Args:
        image_data (bytes): Raw image data
    Returns:
        str: Direct link to uploaded image or None if failed

    
    """
    try:
        upload_url = "https://im.ge/api/1/upload"
        api_key = os.getenv('IMGE_API_KEY')
        
        # Prepare the image data
        files = {
            "source": ("image.jpg", image_data, "image/jpeg")
        }
        headers = {"X-API-Key": api_key}
        
        # Upload image
        response = requests.post(upload_url, files=files, headers=headers)
        response.raise_for_status()
        
        # Extract direct link
        upload_data = response.json()
        if "image" in upload_data and "url" in upload_data["image"]:
            return upload_data["image"]["url"]
        
        logger.error("Invalid response format from im.ge")
        return None

    except Exception as e:
        logger.error("Error uploading image to im.ge: %s", str(e))
        return None

def handle_attachment(attachment_data, attachment_type="image"):
    """
    Process attachments (currently supporting images) using Gemini API.
    
    Args:
        attachment_data: Raw attachment data
        attachment_type (str): Type of attachment (currently only 'image' supported)
    Returns:
        str: AI-generated response about the attachment
    """
    if attachment_type != "image":
        return "🚫 Sorry, I currently only support image attachments."
        
    try:
        logger.info("Processing image attachment")
        
        # Upload image to im.ge
        image_url = upload_image_to_imge(attachment_data)
        if not image_url:
            return "🚫 Failed to process the image. Please try again later."
            
        # Download image for local processing with Gemini
        image_response = requests.get(image_url)
        image_response.raise_for_status()
        image = Image.open(BytesIO(image_response.content))
        
        # Initialize Gemini model for image analysis
        model = get_gemini_model("gemini-1.5-pro")  # Using pro model for better image understanding
        
        # Create prompt for image analysis
        prompt = """Please analyze this image thoroughly and provide:
        1. A detailed description of what you see
        2. If it's a plant, include its botanical name and scientific details
        3. Any notable features or elements
        4. The context or potential use of the image
        
        Be comprehensive but concise in your analysis."""
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        return f"""🖼️ Image Analysis:
{response.text}

🔗 View Image: {image_url}"""

    except Exception as e:
        logger.error("Error processing image: %s", str(e))
        return "🚨 Sorry, I encountered an error processing your image. Please try again later."

def handle_text_command(command_name):
    """
    Handle text commands by importing from CMD folder.
    
    Args:
        command_name (str): Name of the command to execute
    Returns:
        str: Command execution result
    """
    try:
        cmd_module = importlib.import_module(f"CMD.{command_name}")
        return cmd_module.execute()
    except ImportError:
        logger.warning("Command not found: %s", command_name)
        return "🚫 Command not found. Type /help to view available commands."
    except Exception as e:
        logger.error("Error executing command %s: %s", command_name, str(e))
        return "🚨 Error executing command. Please try again later."
