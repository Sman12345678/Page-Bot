import requests
from io import BytesIO
import logging
import os

# Configure logging
logging.basicConfig(
    filename="lyrics_command.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

Info = {
    "Description": "Get lyrics for a song. Usage: /lyrics <song name>"
}

def execute(message, sender_id=None):
    """
    Fetches lyrics from the API and returns the thumbnail image first, then the lyrics text.
    Args:
        message (str): The song name or query.
        sender_id (str): The ID of the user making the request.

    Returns:
        list: [image dict, text dict] on success, or error dict on failure.
    """
    if not message:
        return {"success": False, "type": "text", "data": "❌ Please provide the song name or lyrics query."}

    try:
        logging.info(f"Fetching lyrics for: {message}")
        
        api_url = f"https://kaiz-apis.gleeze.com/api/lyrics?title={message}&apikey=83248daa-8ad2-45d0-93d5-c1c8752b97d3"
      
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            # Download the thumbnail image
            img_response = requests.get(data["thumbnail"])
            if img_response.status_code == 200:
                image_data = BytesIO(img_response.content)
                image_data.seek(0)
                image_msg = {
                    "success": True,
                    "type": "image",
                    "data": image_data
                }
            else:
                logging.warning("Failed to download thumbnail image.")
                image_msg = {"success": False, "type": "text", "data": "⚠️ Unable to fetch the song thumbnail image."}

            # Prepare the lyrics message (plain text)
            text_msg = {
                "success": True,
                "type": "text",
                "data": (
                    f"🎵 {data.get('title', 'No Title')}\n"
                    f"👤 Author: {data.get('author', 'Unknown')}\n\n"
                    f"{data.get('lyrics', 'No lyrics found.')}\n"
                    "________________________\n"
                    "Powered by Kora AI | Source: Kaiz Lyrics API"
                )
            }

            return [image_msg, text_msg]
        else:
            logging.error(f"Lyrics API returned {response.status_code}: {response.text}")
            return {"success": False, "type": "text", "data": "🚨 Could not fetch lyrics. Please try again later."}
    except Exception as e:
        logging.error(f"Error fetching lyrics: {str(e)}")
        return {"success": False, "type": "text", "data": f"🚨 An error occurred: {str(e)}"}
