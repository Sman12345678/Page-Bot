import requests
from io import BytesIO
import time
import logging

Info = {
    "Description": "Generate image based on prompt"
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def execute(message):
    logging.info("Executing image generation with message: %s", message)
    try:
        # API endpoint
        api_url = f"(https://mahi-apis.onrender.com/api/fluxpro?prompt={message})"
        logging.info("API URL: %s", api_url)

        # Sending GET request
        response = requests.get(api_url)
        logging.info("Response Status Code: %d", response.status_code)

        if response.status_code == 200:
            result = response.json()
            logging.info("API Response: %s", result)

            # Simulate processing time
            time.sleep(5)
            logging.info("Simulated processing time completed")

            # Download each image as bytes
            images = []
            for item in result['data']:
                img_url = item['imageUrl']
                logging.info("Downloading image from: %s", img_url)
                img_response = requests.get(img_url)

                if img_response.status_code == 200:
                    images.append(BytesIO(img_response.content))
                    logging.info("Successfully downloaded image from: %s", img_url)
                else:
                    error_message = f"Failed to download image from {img_url}"
                    logging.error(error_message)
                    return {"success": False, "message": error_message}

            logging.info("Image generation successful")
            return {"success": True, "images": images}
        else:
            error_message = f"API error: {response.status_code}"
            logging.error(error_message)
            return {"success": False, "message": error_message}

    except requests.exceptions.RequestException as e:
        error_message = f"Request error: {str(e)}"
        logging.error(error_message)
        return {"success": False, "message": error_message}

    except Exception as e:
        error_message = f"Unexpected error: {str(e)}"
        logging.error(error_message)
        return {"success": False, "message": error_message}

# Running the function
