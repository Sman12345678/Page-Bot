import requests
from io import BytesIO

Info = {
    "Description": "Generate an image based on the given prompt using the custom API."
}

def execute(message):
    """
    Generate an image based on the given prompt using the custom API.

    Args:
        message (str): The user's prompt to generate an image.

    Returns:
        dict: Contains success status and image data or error message.
    """
    if not message:
        return [{"success": False, "data": "❌ Please Provide a Prompt After That Command "}]

    try:
        # Custom API endpoint
        api_url = f"https://kaiz-apis.gleeze.com/api/flux?prompt={message}"

        # Sending the prompt to the API
        response = requests.get(api_url)

        if response.status_code == 200:
            # Get the image as bytes
            image_data = BytesIO(response.content)
            awaiting="🎨 Kora is generating Your Image..."
            return {"awaiting":awaiting,"success": True, "data": image_data}

        else:
            return {"success": False, "data": "🚨 Failed to generate the image. Please try again later."}

    except Exception as e:
        return {"success": False, "data": f"🚨 An error occurred: {str(e)}"}
