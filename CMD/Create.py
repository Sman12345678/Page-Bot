import requests
from io import BytesIO
from bs4 import BeautifulSoup  # Ensure BeautifulSoup is imported
import logging

# Configure logging
logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def execute(message):
    """
    Scrapes images from Bing based on the search term (message) and returns the first 5 images as BytesIO objects.
    
    :param message: Search term to fetch images.
    :return: List of dictionaries containing success status and image data or error message.
    """
    if not message:
        return [{"success": False, "data": "❌ Please Provide a Search Term After That Command "}]

    url = f"https://www.bing.com/images/search?q={message}"
    logging.info(f"Fetching URL: {url}")
    
    try:
        # Send a GET request to fetch the webpage
        response = requests.get(url)
        response.raise_for_status()
        logging.info(f"Successfully fetched the webpage for search term: {message}")
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch webpage: {e}")
        return [{"success": False, "data": f"🚨 Failed to fetch webpage: {str(e)}"}]
    
    # Parse the webpage content
    soup = BeautifulSoup(response.content, 'html.parser')
    image_tags = soup.find_all('img', class_=['mimg', 'rms_img', 'vimgld'])
    if not image_tags:
        logging.warning(f"No images found for search term: {message}")
        return [{"success": False, "data": "🚨 No images found for the search term."}]
    
    images = []
    for i, img_tag in enumerate(image_tags[9:14]):  # Limit to the first 5 images
        src = img_tag.get('src')
        if not src:
            logging.warning(f"Image tag {i + 1} has no 'src' attribute.")
            continue
        
        try:
            # Fetch the image
            img_response = requests.get(src)
            img_response.raise_for_status()
            image_data = BytesIO(img_response.content)  # Get the image data as bytes
            images.append({"success": True, "data": image_data})
            logging.info(f"Image {i + 1} fetched successfully from: {src}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch image {i + 1} from {src}: {e}")
            images.append({"success": False, "data": f"🚨 Failed to fetch image {i + 1} from {src}: {str(e)}"})
    
    logging.info(f"Total images fetched: {len(images)}")
    return images
