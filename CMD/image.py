import requests
import urllib.parse

# Info dictionary for help command
Info = {
    "Description": "Generate images based on a prompt"
}

def execute(prompt):
    # Check if prompt is empty
    if not prompt:
        return "Please provide a prompt after the /image command."

    # Send awaiting message
    awaiting_message = "🖼️ Generating your image, please wait..."

    # URL encode the prompt for the API request
    encoded_prompt = urllib.parse.quote(prompt)
    api_url = f"https://priyansh-ai.onrender.com/txt2img?prompt={encoded_prompt}&apikey=priyansh-here"

    try:
        # Make the request to the image generation API
        response = requests.get(api_url)
        response_data = response.json()

        # Check for a successful response and an image URL in the result
        if response.status_code == 200 and "image_url" in response_data:
            image_url = response_data["image_url"]
            return f"Here is your generated image:\n{image_url}"
        else:
            return "Sorry, there was an issue generating the image. Please try again later."
    except requests.RequestException as e:
        # Log error and return a failure message
        print(f"Error while requesting image: {e}")
        return "An error occurred while trying to generate the image. Please try again."
