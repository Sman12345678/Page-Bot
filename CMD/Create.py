import requests
from io import BytesIO

def execute(message):
    """
    Generate an image based on the given prompt using ClashAI's DALL-E-3 API.

    Args:
        message (str): The prompt to generate an image.

    Returns:
        dict: Contains success status and either the image data or an error message.
    """
    api_key = "sk-C3eN21tQ11SZxvAqpGsm1FqAYdvdX9wreD5c6MrVBNCxrhQv"
    url = "https://api.clashai.eu/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "dall-e-3",
        "prompt": message,
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
                        return {"success": True, "data": BytesIO(image_response.content)}
                    else:
                        return {"success": False, "error": f"Failed to fetch the image from URL: {image_url}"}
            else:
                return {"success": False, "error": "No image data received from the API."}
        else:
            return {"success": False, "error": f"API returned an error: {response.status_code}, {response.text}"}
    except Exception as e:
        return {"success": False, "error": f"An exception occurred: {str(e)}"}
