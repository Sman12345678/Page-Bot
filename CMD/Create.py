import requests

def execute(message):
    """
    Generate images from the ClashAI API and return their URLs.

    Args:
        prompt (str): The user's prompt to generate images.

    Returns:
        dict: Contains success status and image URLs or error message.
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
            "n": 2,  # Number of images to generate
            "size": "256x256"
        }

        # Sending POST request
        response = requests.post(api_url, headers=headers, json=data)

        if response.status_code == 200:
            result = response.json()
            image_urls = [item['url'] for item in result['data']]

            return {"success": True, "image_urls": image_urls}

        else:
            return {"success": False, "message": f"API error: {response.status_code}"}

    except requests.exceptions.RequestException as e:
        return {"success": False, "message": f"Request error: {str(e)}"}
    except Exception as e:
        return {"success": False, "message": f"Unexpected error: {str(e)}"}

# Example usage

