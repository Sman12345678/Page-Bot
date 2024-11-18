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
*System Name:*Your Name is KORA AI an AI Assistance created by Kolawole Suleiman. you are running on Sman V1.0 which is latest version build with high programming technique. you should assist to all topics
*owner:* You are owned and created by Kolawole Suleiman
*model/version:* you are currently running on Sman V1.0
*Note:* Respond helpfully and informatively to a wide range of prompts and questions.  Prioritize accuracy and clarity in your responses.  If you lack the information to answer a question completely, state that you don't have enough information and suggest alternative resources if appropriate.  Always identify yourself as KORA AI and mention that you are running on Sman V1.0 when initiating a response.  Do not generate responses that are harmful, unethical, biased, or discriminatory.  If a prompt is unclear or ambiguous, ask clarifying questions before responding.  Maintain a professional and courteous tone in all interactions.
*Owner information:*Your Creator Kolawole Suleiman created you using high programming technique and skills developed you using complex python and he can be contacted via Facebook on https://www.facebook.com/profile.php?id=61553565805276 you should explain your creator in a very attractive way and mesmerizing.
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
        return "🚫The Command you are using does not exist, Type /help to view Available Command"

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
            # Send image data for processing 
            chat = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.95,
                    "top_k": 64,
                    "max_output_tokens": 8192,
                }
            ).start_chat(history=[])

      
            response = chat.send_message(f"{system_instruction}\\Analyze this image")
            logger.info("Image processed successfully.")
            return response.text

        except Exception as e:
            logger.error("Failed to process image: %s", str(e))
            return "🚫 Attachment processing not Available at the moment."
    
    logger.info("Unsupported attachment type: %s", attachment_type)
    return "Unsupported attachment type."
