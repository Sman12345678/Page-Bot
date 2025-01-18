from io import BytesIO
from bs4 import BeautifulSoup
import requests
import logging
import app as Suleiman
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
sender_id=" "
def execute(message):
    """
    Scrapes an image from Bing based on the search term and uploads it to Facebook.

    :param message: Search term for Bing image search.
    :return: Sends a message with the uploaded image or an error message.
    """
    if not message.strip():
        return [{"success": False, "data": "❌ Please provide a valid search term."}]

    url = f"https://www.bing.com/images/search?q={message}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        # Fetch Bing search results
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch webpage: {e}")
        Suleiman.send_message(sender_id, f"🚨 Failed to fetch webpage: {str(e)}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    image_tags = soup.find_all('img', class_=['mimg', 'rms_img', 'vimgld'])
    if not image_tags:
        Suleiman.send_message(sender_id, "🚨 No images found for the search term.")
        return

    # Fetch the first valid image
    for img_tag in image_tags:
        src = img_tag.get('src') or img_tag.get('data-src')
        if not src:
            continue
        src = urljoin("https://www.bing.com", src)

        try:
            img_response = requests.get(src, headers=headers)
            img_response.raise_for_status()
            image_data = BytesIO(img_response.content)

            # Upload the image to Facebook
            upload_response = Suleiman.upload_image_to_graph(image_data)

            if upload_response.get("success"):
                attachment_id = upload_response.get("attachment_id")
                Suleiman.send_message(sender_id, {
                    "attachment": {
                        "type": "image",
                        "payload": {"attachment_id": attachment_id}
                    }
                })
                return
            else:
                Suleiman.send_message(sender_id, f"🚨 Failed to upload image. Error: {upload_response.get('error')}")
                return
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch image from {src}: {e}")
            Suleiman.send_message(sender_id, f"🚨 Failed to fetch image: {str(e)}")
            return

    Suleiman.send_message(sender_id, "🚨 No valid images found.")
