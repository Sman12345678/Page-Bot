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
        "apikey": "83248daa-8ad2-45d0-93d5-c1c8752b97d3"
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
        # Always include the text response first
        if text_response:
            messages.append({
                "success": True,
                "type": "text",
                "data": text_response
            })

        # Only include the image if it exists
        if image_url:
            try:
                img_response = requests.get(image_url, stream=True, timeout=30)
                if img_response.status_code == 200:
                    image_bytes = BytesIO(img_response.content)
                    messages.insert(0, {  # Insert image before text (optional, or after if you want text first)
                        "success": True,
                        "type": "image",
                        "data": image_bytes
                    })
                else:
                    messages.insert(0, {
                        "success": False,
                        "type": "text",
                        "data": "❌ Failed to fetch the generated image."
                    })
            except Exception as e:
                messages.insert(0, {
                    "success": False,
                    "type": "text",
                    "data": f"🚨 Error fetching image: {str(e)}"
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
