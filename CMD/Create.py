import requests
from io import BytesIO

def execute(message=None):
    """
    Generate images using the ClashAI DALL-E-3 API.

    Args:
        message (str): The prompt for image generation.

    Returns:
        dict: A dictionary containing success status and either the images or an error message.
    """
    if not message:
        return {"success": False, "data": "🚨 No prompt provided. Please provide a valid prompt for image generation."}

    url = "https://api.clashai.eu/v1/images/generations"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer sk-C3eN21tQ11SZxvAqpGsm1FqAYdvdX9wreD5c6MrVBNCxrhQv"
    }
    data = {
        "model": "dall-e-3",
        "prompt": message,
        "n": 2,
        "size": "256x256"
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            images = []
            for img_data in result.get('data', []):
                img_url = img_data.get('url')
                if img_url:
                    img_response = requests.get(img_url)
                    if img_response.status_code == 200:
                        img = BytesIO(img_response.content)
                        images.append(img)
                    else:
                        return {"success": False, "data": f"🚨 Failed to fetch image from URL: {img_url}"}
            return {"success": True, "images": images}
        else:
            return {
                "success": False,
                "data": f"🚨 Error from API. Status code: {response.status_code}, Response: {response.text}"
            }
    except requests.exceptions.RequestException as e:
        return {"success": False, "data": f"🚨 Request failed: {str(e)}"}
