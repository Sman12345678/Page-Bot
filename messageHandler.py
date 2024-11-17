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
        return "The Command you are using does not exist."

# Handle attachments (e.g., direct images)
def handle_attachement(arch_file)
    try:
        # Upload to im.ge
        arch_api_key = os.getenv('ARCH_UPLOAD_API_KEY')
        if not arch_api_key:
            raise ValueError("ARCH_UPLOAD_API_KEY is not set in the environment.")

        arch_upload_url = 'https://im.ge/api/1/upload'
        arch_payload = {'source': (arch_file.filename, arch_file.read(), arch_file.content_type)}
        arch_headers = {'X-API-Key': arch_api_key}

        arch_response = requests.post(arch_upload_url, files=arch_payload, headers=arch_headers, verify=False)
        arch_response.raise_for_status()  # Raise error if the request fails

        arch_image_url = arch_response.json().get('image', {}).get('url')
        if not arch_image_url:
            raise ValueError("No image URL returned from im.ge API.")

        logger.info(f"Image successfully uploaded: {arch_image_url}")

        # Analyze with Gen AI
        model = GenerativeModel("gemini-1.5-pro")
        arch_image_data = requests.get(arch_image_url, verify=False).content

        arch_analysis_request = model.generate_content([
            "Analyze the image thoroughly. Suggest taking a better shot if details are unclear. "
            "If it's a plant, provide its scientific answer with humor and professionalism. "
            "Dismiss cartoon images humorously while emphasizing the importance of real images.",
            {'mime_type': 'image/jpeg', 'data': arch_image_data}
        ])

        arch_analysis = arch_analysis_request.text

        logger.info("Image analyzed successfully.")
        return jsonify({'image_url': arch_image_url, 'analysis': arch_analysis})

    except requests.RequestException as arch_error:
        arch_message = f"Request failed: {str(arch_error)}"
        logger.error(f"Request error: {arch_message}\n{traceback.format_exc()}")
        return jsonify({'error': arch_message}), 500

    except Exception as e:
        arch_message = f"Unexpected error: {str(e)}"
        logger.error(f"Unexpected error: {arch_message}\n{traceback.format_exc()}")
        return jsonify({'error': arch_message}), 500
