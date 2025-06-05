import requests
import logging
import time
import app  # To use app.report

# Track last used time and in-progress state per user
user_last_used = {}
in_progress = set()

Info = {
    "Description": "Generate Images using Bing Creator API"
}

GEN_ENDPOINT = "https://bing-image-creator-0255.onrender.com/api/gen"

logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

COOLDOWN_SECONDS = 10

def execute(message, sender_id=None):
    try:
        if not message or not message.strip():
            return {
                "success": False,
                "type": "text",
                "data": "❌ Please provide a valid prompt for image generation."
            }

        # In-progress check
        if sender_id is not None:
            if sender_id in in_progress:
                return {
                    "success": False,
                    "type": "text",
                    "data": "⏳ Your previous /bing request is still in progress. Please wait for it to finish."
                }

            # Cooldown check
            now = time.time()
            last_used = user_last_used.get(sender_id, 0)
            if now - last_used < COOLDOWN_SECONDS:
                wait_time = int(COOLDOWN_SECONDS - (now - last_used))
                return {
                    "success": False,
                    "type": "text",
                    "data": f"⏳ Please wait {wait_time} seconds before using /bing again. This command has a 10 second cooldown."
                }
            # Mark as in progress
            in_progress.add(sender_id)
            user_last_used[sender_id] = now

        # Send waiting message as part of the response
        waiting_msg = {
            "success": True,
            "type": "text",
            "data": "🎨 Generating your images, please wait... ⏳"
        }

        params = {"prompt": message, "api_key": "sman-apiA1B2C3D4E5"}
        try:
            response = requests.get(GEN_ENDPOINT, params=params, timeout=120)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            app.report(f"Bing API Error: {str(e)}")
            return [
                waiting_msg,
                {
                    "success": False,
                    "type": "text",
                    "data": "❌ Bing image generation failed. Please try again later."
                }
            ]
        finally:
            if sender_id is not None:
                in_progress.discard(sender_id)

        if not isinstance(result, list) or not result:
            return [
                waiting_msg,
                {
                    "success": False,
                    "type": "text",
                    "data": "❌ No images were generated. Please try again with a different prompt."
                }
            ]

        images = [waiting_msg]
        for item in result:
            url = item.get("url")
            if not url:
                continue
            images.append({
                "success": True,
                "type": "image_url",
                "data": url
            })

        if images:
            return images
        else:
            return [
                waiting_msg,
                {
                    "success": False,
                    "type": "text",
                    "data": "❌ Failed to fetch generated images."
                }
            ]
    except Exception as e:
        if sender_id is not None:
            in_progress.discard(sender_id)
        app.report(f"Unexpected error in bing.py: {str(e)}")
        return {
            "success": False,
            "type": "text",
            "data": f"❌ An unexpected error occurred: {str(e)}"
        }
