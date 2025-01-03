import requests
from io import BytesIO

def execute(message):
    """
    Generate an image based on the given prompt using ClashAI's DALL-E-3 API.

    Args:
        message (dict): A dictionary containing 'type' and 'content' keys.

    Returns:
        dict: Contains success status and message with 'type' and 'content' keys.
    """
    # Validate message input
    if not isinstance(message, dict) or "type" not in message or "content" not in message:
        return {
            "success": False,
            "message": {
                "type": "text",
                "content": "🚨 Invalid message format. Expected a dictionary with 'type' and 'content' keys."
            }
        }

    if message["type"] != "text":
        return {
            "success": False,
            "message": {
                "type": "text",
                "content": "🚨 Unsupported message type. Only 'text' is supported."
            }
        }

    prompt = message["content"]
    api_key = "sk-C3eN21tQ11SZxvAqpGsm1FqAYdvdX9wreD5c6MrVBNCxrhQv"
    url = "https://api.clashai.eu/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "dall-e-3",
        "prompt": prompt,
        "n": 1,
        "size": "256x256"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            if "data" in result and result["data"]:
                image_url = result["data"][0].get("url")
                if image_url:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        return {
                            "success": True,
                            "message": {
                                "type": "image",
                                "content": BytesIO(image_response.content)
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "message": {
                                "type": "text",
                                "content": f"🚨 Failed to fetch the image from URL: {image_url}"
                            }
                        }
            else:
                return {
                    "success": False,
                    "message": {
                        "type": "text",
                        "content": "🚨 No image data received from the API."
                    }
                }
        else:
            return {
                "success": False,
                "message": {
                    "type": "text",
                    "content": f"🚨 API returned an error: {response.status_code}, {response.text}"
                }
            }
    except Exception as e:
        return {
            "success": False,
            "message": {
                "type": "text",
                "content": f"🚨 An exception occurred: {str(e)}"
            }
        }
