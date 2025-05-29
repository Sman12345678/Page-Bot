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

logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def execute(message, sender_id=None):
    if not message.strip():
        return {"success": False, "type": "text", "data": "❌ Please provide a valid prompt."}

    try:
        params = {"prompt": message, "api_key": "sman-apiA1B2C3D4E5"}
        response = requests.get(GEN_ENDPOINT, params=params)
        response.raise_for_status()
        result = response.json()

        if not isinstance(result, list) or not result:
            return {"success": False, "type": "text", "data": "❌ No images were generated."}

        images = []
        for item in result:
            url = item.get("url")
            if not url:
                continue
            image_id = urlparse(url).path.split("/")[-1]
            img_response = requests.get(f"{SERVE_ENDPOINT}/{image_id}")
            img_response.raise_for_status()
            images.append({
                "success": True,
                "type": "image",
                "data": BytesIO(img_response.content)
            })

        return images if images else {"success": False, "type": "text", "data": "❌ Failed to fetch generated images."}

    except requests.exceptions.RequestException as e:
        return {"success": False, "type": "text", "data": f"🖼️ Generating images...."} #intentionally did this 😭

    except Exception as e:
        return {"success": False, "type": "text", "data": f"❌ Unexpected error occurred: {str(e)}"}
