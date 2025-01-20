from io import BytesIO
from bs4 import BeautifulSoup
import requests
import logging
from urllib.parse import urljoin
import app as Suleiman 

# Configure logging
logging.basicConfig(
    filename="image_scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def fetch_image_from_graph(attachment_id):
    url = f"https://graph.facebook.com/v21.0/{attachment_id}"
    params = {"access_token": Suleiman.PAGE_ACCESS_TOKEN}

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            image_url = response.json().get("url")
            if image_url:
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                return {"success": True, "image_data": image_response.content}
            else:
                return {"success": False, "error": "No URL found in response"}
        else:
            logging.error("Failed to fetch image: %s", response.json())
            return {"success": False, "error": response.json()}
    except Exception as e:
        logging.error("Error in fetch_image_from_graph: %s", str(e))
        return {"success": False, "error": str(e)}

def execute(message):
    """
    Scrapes images from Bing based on the search term and uploads them to the graph.

    :param message: Search term to fetch images.
    :return: List of dictionaries containing success status and image data or error message.
    """
    if not message.strip():
        return [{"success": False, "data": "❌ Please provide a valid search term."}]

    url = f"https://www.bing.com/images/search?q={message}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    logging.info(f"Fetching URL: {url}")
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to fetch webpage: {e}")
        return [{"success": False, "data": f"🚨 Failed to fetch webpage: {str(e)}"}]
    
    soup = BeautifulSoup(response.content, 'html.parser')
    image_tags = soup.find_all('img', class_=['mimg', 'rms_img', 'vimgld'])
    if not image_tags:
        return [{"success": False, "data": "🚨 No images found for the search term."}]

    results = []
    for i, img_tag in enumerate(image_tags[9:14]):  # Fetch the first 5 images
        src = img_tag.get('src') or img_tag.get('data-src')
        if not src:
            continue
        src = urljoin("https://www.bing.com", src)

        try:
            img_response = requests.get(src, headers=headers)
            img_response.raise_for_status()
            image_data = BytesIO(img_response.content)
            upload_response = Suleiman.upload_image_to_graph(image_data)

            if upload_response["success"]:
                attachment_id = upload_response["attachment_id"]
                image_fetch_response = fetch_image_from_graph(attachment_id)
                if image_fetch_response["success"]:
                    results.append({
                        "success": True,
                        "data": f"Image {i + 1} uploaded and fetched successfully.",
                        "upload_response": upload_response,
                        "fetched_image_data": image_fetch_response["image_data"]
                    })
                    logging.info(f"Image {i + 1} fetched and uploaded successfully from: {src}")
                else:
                    results.append({
                        "success": False,
                        "data": f"🚨 Failed to fetch image {i + 1} using attachment ID: {attachment_id}",
                        "error": image_fetch_response["error"]
                    })
            else:
                results.append({
                    "success": False,
                    "data": f"🚨 Failed to upload image {i + 1}.",
                    "upload_response": upload_response
                })
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch image {i + 1} from {src}: {e}")
            results.append({"success": False, "data": f"🚨 Failed to fetch image {i + 1}: {str(e)}"})
        except Exception as e:
            logging.error(f"Error uploading image {i + 1}: {e}")
            results.append({"success": False, "data": f"🚨 Error uploading image {i + 1}: {str(e)}"})

    return results
