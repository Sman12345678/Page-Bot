import os
import requests

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
ADMIN_ID = os.getenv("ADMIN_ID")

def post_text_to_page(message):
    url = "https://graph.facebook.com/v22.0/me/feed"
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def post_image_to_page(image_url, caption=""):
    url = "https://graph.facebook.com/v22.0/me/photos"
    payload = {
        "url": image_url,
        "caption": caption,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def execute(message, sender_id):
    if sender_id != ADMIN_ID:
        return "⛔ Unauthorized user. Only the admin can post."

    message = message.strip()

    if not message:
        return "⚠️ Message cannot be empty. Please provide a valid message."

    # Handle image post: "image IMAGE_URL|Caption text"
    if message.lower().startswith("image "):
        try:
            command_content = message[6:].strip()  # remove "image "

            if "|" not in command_content:
                return "⚠️ Invalid format. Use: image IMAGE_URL|Caption text"

            image_url, caption = command_content.split("|", 1)
            image_url = image_url.strip()
            caption = caption.strip()

            if not image_url:
                return "⚠️ Image URL is missing. Format: image IMAGE_URL|Caption"

            if not caption:
                return "⚠️ Caption is missing. Format: image IMAGE_URL|Caption"

            result = post_image_to_page(image_url, caption)
            return (
                f"✅ Image posted successfully.\n"
                f"🖼️ Image URL: {image_url}\n"
                f"📝 Caption: {caption}\n"
                f"📡 Facebook Response: {result}"
            )

        except Exception as e:
            return f"❌ Error posting image: {str(e)}"

    # Default: treat as text post
    try:
        result = post_text_to_page(message)
        return (
            f"✅ Text posted successfully.\n"
            f"📝 Message: {message}\n"
            f"📡 Facebook Response: {result}"
        )
    except Exception as e:
        return f"❌ Error posting text: {str(e)}"
