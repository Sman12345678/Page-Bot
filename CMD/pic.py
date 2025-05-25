from io import BytesIO
import requests
import logging
from urllib.parse import urlparse

Info = {
    "Description": "Generate Images using Bing Creator API"
}

API_BASE = "https://bing-image-creator-0255.onrender.com"
GEN_ENDPOINT = f"{API_BASE}/api/gen"
SERVE_ENDPOINT = f"{API_BASE}/serve-image"

# Configure logging
logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def execute(message, sender_id=None):
    """
    Uses Bing Image Creator API to generate images and returns them as BytesIO streams.

    :param message: The prompt for image generation.
    :return: List of image dicts or error message.
    """
    if not message.strip():
        return {"success": False, "type": "text", "data": "❌ Please provide a valid prompt."}

    try:
        # Step 1: Call the image generation API
        logging.info(f"🔁 Sending prompt to generation API: {message}")
        response = requests.post(GEN_ENDPOINT, json={"prompt": message, "api_key": "sman-apiA1B2C3D4E5"})  # Replace key if needed
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, list) or not result:
            logging.warning("❌ No images returned.")
            return {"success": False, "type": "text", "data": "❌ No images were generated."}

        images = []

        # Step 2: Download each image by ID
        for item in result:
            url = item.get("url")
            if not url:
                continue

            image_id = urlparse(url).path.split("/")[-1]
            image_url = f"{SERVE_ENDPOINT}/{image_id}"
            logging.info(f"⬇️ Downloading image from: {image_url}")

            img_response = requests.get(image_url)
            img_response.raise_for_status()

            images.append({
                "success": True,
                "type": "image",
                "data": BytesIO(img_response.content)
            })

        return images if images else {"success": False, "type": "text", "data": "❌ Failed to fetch generated images."}

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP error: {e}")
        return {"success": False, "type": "text", "data": f"🚨 Request failed: {str(e)}"}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return {"success": False, "type": "text", "data": f"❌ Unexpected error occurred: {str(e)}"}
