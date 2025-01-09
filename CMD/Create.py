import requests
from io import BytesIO
import time

def execute(message):
    try:
        # Return awaiting message
        yield {"success": True, "message": "🎨 Generating image..."}

        # API endpoint
        api_url = f"(https://mahi-apis.onrender.com/api/fluxpro?prompt={message})"

        # Sending GET request
        response = requests.get(api_url)

        if response.status_code == 200:
            result = response.json()

            # Simulate processing time
            time.sleep(5)

            # Download each image as bytes
            images = []
            for item in result['data']:
                img_url = item['imageUrl']
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
