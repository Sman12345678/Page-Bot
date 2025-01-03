import requests
from io import BytesIO

def execute(message):
    """
    Generate an image from the ClashAI API, download it, and return the image.

    Args:
        prompt (str): The user's prompt to generate the image.

    Returns:
        dict: Contains success status and the downloaded image or an error message.
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
            "n": 1,  # Only one image is generated
            "size": "256x256"
        }

        # Sending POST request
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            image_url = result['data'][0]['url']  # Get the first image URL

            # Download the image
            img_response = requests.get(image_url)
            if img_response.status_code == 200:
                # Return the downloaded image content as bytes
                return {"success": True, "image": img_response.content}
            else:
                return {"success": False, "message": "Failed to download the image."}
        
        else:
            return {"success": False, "message": f"API error: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Request error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

# Example usage
