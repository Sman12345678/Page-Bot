import requests
from io import BytesIO

Info = {
    "Description": "Generate an image based on the given prompt using ClashAI's DALL-E-3 API."
}

def execute(message):
    """
    Generate an image based on the given prompt using ClashAI's DALL-E-3 API.

    Args:
        message (str): The user's prompt to generate an image.

    Returns:
        dict: Contains success status and image data or error message.
    """
    try:
        # Custom API endpoint
        api_url = "https://api.clashai.eu/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-C3eN21tQ11SZxvAqpGsm1FqAYdvdX9wreD5c6MrVBNCxrhQv"
        }
        data = {
            "model": "dall-e-3",
            "prompt": message,
            "n": 1,
            "size": "256x256"
        }

        # Sending the prompt to the API
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            if "data" in result and result["data"]:
                image_url = result["data"][0].get("url")
                if image_url:
                    image_response = requests.get(image_url)
                    if image_response.status_code == 200:
                        image_data = BytesIO(image_response.content)
                        awaiting = "🎨 Kora is generating your image..."
                        return {"success": True, "data": image_data, "await": awaiting}
                    else:
                        return {"success": False, "data": f"🚨 Failed to fetch the image from URL: {image_url}"}
            else:
                return {"success": False, "data": "🚨 No image data received from the API."}
        else:
            return {"success": False, "data": f"🚨 API returned an error: {response.status_code}, {response.text}"}

    except Exception as e:
        return {"success": False, "data": f"🚨 An error occurred: {str(e)}"}
