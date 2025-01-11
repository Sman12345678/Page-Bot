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

def upload_image_to_graph(image_data):
    """
    Uploads an image to Facebook and returns its attachment ID.
    
    :param image_data: The image data as BytesIO.
    :return: A dictionary with success status and attachment ID or error message.
    """
    url = "https://graph.facebook.com/v21.0/me/message_attachments"
    params = {"access_token": os.getenv("PAGE_ACCESS_TOKEN")}
    files = {"filedata": ("image.jpg", image_data, "image/jpeg")}
    data = {"message": '{"attachment":{"type":"image", "payload":{}}}'}
    
    try:
        response = requests.post(url, params=params, files=files, data=data)
        response.raise_for_status()
        result = response.json()
        return {"success": True, "attachment_id": result.get("attachment_id")}
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to upload image to Facebook: {e}")
        return {"success": False, "data": f"🚨 Error uploading image: {str(e)}"}

def execute(message):
    """
    Scrapes images from Bing based on the search term and uploads them to Facebook.
    
    :param message: Search term to fetch images.
    :return: List of dictionaries containing success status and attachment ID or error message.
    """
    if not message:
        return [{"success": False, "data": "❌ Please provide a search term after that command."}]

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
    for i, img_tag in enumerate(image_tags[:5]):  # Fetch the first 5 images
        src = img_tag.get('src')
        if not src:
            logging.warning(f"Image tag {i + 1} has no 'src' attribute.")
            continue
        
        try:
            # Fetch the image
            img_response = requests.get(src)
            img_response.raise_for_status()
            image_data = BytesIO(img_response.content)  # Get the image data as bytes
            
            # Upload the image to Facebook
            upload_response = upload_image_to_graph(image_data)
            if upload_response.get("success"):
                images.append({"success": True, "data": {"type": "image", "content": upload_response["attachment_id"]}})
            else:
                images.append({"success": False, "data": upload_response["data"]})
            logging.info(f"Image {i + 1} processed successfully from: {src}")
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch image {i + 1} from {src}: {e}")
            images.append({"success": False, "data": f"🚨 Failed to fetch image {i + 1} from {src}: {str(e)}"})
    
    logging.info(f"Total images processed: {len(images)}")
    return images
