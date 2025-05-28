import os
import requests

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")
PAGE_ID = os.getenv("PAGE_ID")

def post_text_to_page(message):
    url = f"https://graph.facebook.com/{PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def post_image_to_page(image_url, caption=""):
    url = f"https://graph.facebook.com/{PAGE_ID}/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def execute(message, sender_id):
    if sender_id != ADMIN_ID:
        return "Unauthorized user."

    # ! Handle image post: "post image IMAGE_URL|caption"
    if message.lower().startswith("post image "):
        try:
            command_content = message[11:].strip()  # remove "post image "
            
            if "|" not in command_content:
                return "Invalid format. Use: post image IMAGE_URL|Caption text"

            image_url, caption = command_content.split("|", 1)
            image_url = image_url.strip()
            caption = caption.strip()

            if not image_url:
                return "Image URL is missing. Format: post image IMAGE_URL|Caption"

            if not caption:
                return "Caption is missing. Format: post image IMAGE_URL|Caption"

            result = post_image_to_page(image_url, caption)
            return f"✅ Image posted.\n🖼️ Image URL: {image_url}\n📝 Caption: {caption}\n📡 Facebook Response: {result}"

        except Exception as e:
            return f"An error occurred while posting image: {str(e)}"

     
