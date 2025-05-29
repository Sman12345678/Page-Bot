import requests
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(
    filename="image_generator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

Info = {
    "Description": "Generate an image based on the given prompt using the custom API."
}

def execute(message,sender_id=None):
    """
    Generate an image based on the given prompt using the custom API.

    Args:
        message (str): The user's prompt to generate an image.

    Returns:
        dict: Contains success status, type, and image data or error message.
    """
    if not message:
        return {"success": False, "type": "text", "data": "❌ Please provide a prompt for image generation"}

    try:
        # Log the generation attempt
        logging.info(f"Attempting to generate image with prompt: {message}")
        
        # Custom API endpoint
        api_url = f"https://kaiz-apis.gleeze.com/api/flux?prompt={message}&apikey=2d91ea21-2c65-4edc-b601-8d06085c8358"
        
        # Send initial message about generation
        initial_response = {"success": True, "type": "text", "data": "🎨 Generating your image..."}
        
        # Sending the prompt to the API
        response = requests.get(api_url)
        
        if response.status_code == 200:
            # Get the image as bytes
            image_data = BytesIO(response.content)
            image_data.seek(0)  # Ensure we're at the start of the buffer
            
            # Log successful generation
            logging.info("Image generated successfully")
            
            # Return list with both text and image responses
            return [
                initial_response,
                {
                    "success": True,
                    "type": "image",
                    "data": image_data
                }
            ]
        else:
            # Log failed attempt
            logging.error(f"API returned status code: {response.status_code}")
            return {"success": False, "type": "text", "data": "🚨 Failed to generate the image. Please try again later."}

    except Exception as e:
        # Log any errors
        logging.error(f"Error generating image: {str(e)}")
        return {"success": False, "type": "text", "data": f"🚨 An error occurred: {str(e)}"}
     
