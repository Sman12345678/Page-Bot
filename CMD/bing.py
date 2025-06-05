from io import BytesIO
import requests
import logging
from urllib.parse import urlparse
import time
import app  # Import app to use app.report

# Track last used time per user to implement cooldown
user_last_used = {}

Info = {
    "Description": "Generate Images using Bing Creator API"
}

API_BASE = "https://bing-image-creator-0255.onrender.com"
GEN_ENDPOINT = f"{API_BASE}/api/gen"
SERVE_ENDPOINT = f"{API_BASE}/serve-image"

logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

COOLDOWN_SECONDS = 10

def execute(message, sender_id=None):
    try:
        # Validate prompt
        if not message or not message.strip():
            return {
                "success": False,
                "type": "text",
                "data": "❌ Please provide a valid prompt for image generation."
            }

        # Cooldown check
        now = time.time()
        if sender_id is not None:
            last_used = user_last_used.get(sender_id, 0)
            if now - last_used < COOLDOWN_SECONDS:
                wait_time = COOLDOWN_SECONDS - (now - last_used)
                return {
                    "success": False,
                    "type": "text",
                    "data": f"⏳ Please wait {int(wait_time)} seconds before using /bing again. This command has a 10 second cooldown."
                }
            user_last_used[sender_id] = now

        params = {"prompt": message, "api_key": "sman-apiA1B2C3D4E5"}
        response = requests.get(GEN_ENDPOINT, params=params, timeout=120)
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, list) or not result:
            return {
                "success": False,
                "type": "text",
                "data": "❌ No images were generated. Please try again with a different prompt."
            }

        images = []
        for item in result:
            url = item.get("url")
            if not url:
                continue
            image_id = urlparse(url).path.split("/")[-1]
            try:
                img_response = requests.get(f"{SERVE_ENDPOINT}/{image_id}", timeout=60)
                img_response.raise_for_status()
                images.append({
                    "success": True,
                    "type": "image",
                    "data": BytesIO(img_response.content)
                })
            except Exception as e:
                error_msg = f"❌ Failed to fetch generated image: {str(e)}"
                images.append({
                    "success": False,
                    "type": "text",
                    "data": error_msg
                })
                app.report(f"Error fetching image from Bing API: {str(e)}")  # Report error

        if images:
            return images
        else:
            return {
                "success": False,
                "type": "text",
                "data": "❌ Failed to fetch generated images."
            }

    except requests.exceptions.Timeout as e:
        app.report(f"Bing API Timeout: {str(e)}")
        return {
            "success": False,
            "type": "text",
            "data": "⏰ The Bing image generator took too long. Please try again later."
        }
    except requests.exceptions.RequestException as e:
        app.report(f"Bing API Request Error: {str(e)}")
        return {
            "success": False,
            "type": "text",
            "data": "❌ Bing image generation failed. Please try again later."
        }
    except Exception as e:
        app.report(f"Unexpected error in bing.py: {str(e)}")
        return {
            "success": False,
            "type": "text",
            "data": f"❌ An unexpected error occurred: {str(e)}"
        }
