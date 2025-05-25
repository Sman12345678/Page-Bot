
import requests
from io import BytesIO
import logging

# Configure logging
logging.basicConfig(
    filename="image_generator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

Info = {
    "Description": "Generate images based on the given prompt using the Bing Image Creator custom API."
}

API_KEY = "sman-apiP6Q7R8S9T0"  # <-- Put your API key here, in quotes!

def execute(message, sender_id=None):
    """
    Generate images based on the given prompt using the Bing Image Creator API.

    Args:
        message (str): The user's prompt to generate images.
        sender_id: (optional, for compatibility)

    Returns:
        list: Contains the initial text message, then a dict for each image.
    """
    if not message:
        return [{"success": False, "type": "text", "data": "❌ Please provide a prompt for image generation"}]

    try:
        logging.info(f"Attempting to generate images with prompt: {message}")

        # Step 1: POST to /api/gen to generate image(s)
        api_url = "https://bing-image-creator-0255.onrender.com/api/gen"
        payload = {
            "api_key": API_KEY,
            "prompt": message
        }
        initial_response = {"success": True, "type": "text", "data": "🎨 Generating your images..."}

        gen_response = requests.post(api_url, json=payload)
        if gen_response.status_code == 200:
            images_info = gen_response.json()
            if not images_info or not isinstance(images_info, list) or not images_info[0].get("url"):
                logging.error(f"API returned unexpected data: {images_info}")
                return [{"success": False, "type": "text", "data": "🚨 No images returned. Please try another prompt."}]

            # Step 2: Retrieve ALL images
            results = [initial_response]
            for img_obj in images_info:
                image_url_path = img_obj.get("url")
                if not image_url_path:
                    continue
                image_id = image_url_path.split("/")[-1]
                serve_url = f"https://bing-image-creator-0255.onrender.com/serve-image/{image_id}"
                img_response = requests.get(serve_url)
                if img_response.status_code == 200:
                    image_data = BytesIO(img_response.content)
                    image_data.seek(0)
                    results.append({
                        "success": True,
                        "type": "image",
                        "data": image_data
                    })
                else:
                    logging.error(f"Image fetch failed for {serve_url}, status: {img_response.status_code}")
            if len(results) == 1:  # Only the initial message, no images
                results.append({"success": False, "type": "text", "data": "🚨 Images could not be retrieved."})
            return results
        else:
            logging.error(f"API returned status code: {gen_response.status_code}, body: {gen_response.text}")
            return [{"success": False, "type": "text", "data": "🚨 Failed to generate the images. Please try again later."}]

    except Exception as e:
        logging.error(f"Error generating images: {str(e)}")
        return [{"success": False, "type": "text", "data": f"🚨 An error occurred: {str(e)}"}]
