import requests
from io import BytesIO

def execute(message):
    """
    Generate and download images from the ClashAI API.

    Args:
        prompt (str): The user's prompt to generate images.

    Returns:
        dict: Contains success status and image bytes or error message.
    """
    try:
        # API endpoint and headers
        api_url = "https://api.clashai.eu/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer sk-C3eN21tQ11SZxvAqpGsm1FqAYdvdX9wreD5c6MrVBNCxrhQv"
        }
        # Request payload
        data = {
            "model": "dall-e-3",
            "prompt": message,
            "n": 1,  # Number of images to generate
            "size": "256x256"
        }

        # Sending POST request
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            images = []

            # Download each image as bytes
            for item in result['data']:
                img_url = item['url']
                img_response = requests.get(img_url)
                if img_response.status_code == 200:
                    images.append(BytesIO(img_response.content))
                else:
                    return {"success": False, "message": f"Failed to download image from {img_url}"}

            return {"success": True, "images": images}

        else:
            return {"success": False, "message": f"API error: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Request error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

# Example usage

