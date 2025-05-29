import requests
from io import BytesIO

Info = {
    "Description": "Generate an image using Kaizenji API. Usage: /imagine <prompt>"
}

def execute(message, sender_id):
    api_url = "https://kaiz-apis.gleeze.com/api/gpt-4o-pro"
    params = {
        "ask": message,
        "uid": "Kora",
        "imageUrl": "",
        "apikey": "2d91ea21-2c65-4edc-b601-8d06085c8358"
    }
    try:
        response = requests.get(api_url, params=params, timeout=30)
        if response.status_code != 200:
            return [
                {
                    "success": False,
                    "type": "text",
                    "data": f"❌ API error: {response.status_code}"
                }
            ]
        data = response.json()
        image_url = data.get("images")
        text_response = data.get("response", "")

        messages = []
        # If image exists, add it first
        if image_url:
            try:
                img_response = requests.get(image_url, stream=True, timeout=30)
                if img_response.status_code == 200:
                    image_bytes = BytesIO(img_response.content)
                    messages.append({
                        "success": True,
                        "type": "image",
                        "data": image_bytes
                    })
                else:
                    messages.append({
                        "success": False,
                        "type": "text",
                        "data": "❌ Failed to fetch the generated image."
                    })
            except Exception as e:
                messages.append({
                    "success": False,
                    "type": "text",
                    "data": f"🚨 Error fetching image: {str(e)}"
                })

        # Always include the text response (after the image, if any)
        if text_response:
            messages.append({
                "success": True,
                "type": "text",
                "data": text_response
            })

        return messages
    except Exception as e:
        return [
            {
                "success": False,
                "type": "text",
                "data": f"🚨 Error: {str(e)}"
            }
        ]
