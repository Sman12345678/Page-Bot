import requests
import random
Info = {
    "Description": "Get Response From Kora AI External API"
}

# Endpoint for Kora AI
KORA_AI_API_URL = "https://kora-ai.onrender.com/koraai?query={}"

# Friendly default responses for when no query is provided
DEFAULT_RESPONSES = [
    "👋 Hello there! How can I assist you today? Type `/ai (your question)` to chat with Kora! 😊",
    "Hey buddy! 😁 Need some help? Just use `/ai (your query)` to start a conversation with Kora!",
    "Hi there! 🤖 I’m here to help. Use `/ai (your question)` and let's get started!",
    "Greetings! 🌟 To ask me anything, type `/ai (your query)` and I'll find the answer for you!",
    "Hello, friend! 🙌 Got a question? Use `/ai (query)` to chat with Kora and get insights!"
]

def execute(query=""):
    # If no query is provided, return a random friendly response
    if not query:
        return random.choice(DEFAULT_RESPONSES)
    
    # Encode the query and prepare the API URL
    encoded_query = requests.utils.quote(query)
    api_url = KORA_AI_API_URL.format(encoded_query)

    try:
        # Send the request to Kora AI's API
        response = requests.get(api_url)
        response_data = response.json()

        # Check if the response is successful and contains a reply
        if response.status_code == 200 and "response" in response_data:
            ai_reply = response_data["response"]
            return format_ai_reply(ai_reply)
        else:
            # Return a message if there's an issue with the API
            return "🚫 Sorry, I'm having trouble reaching Kora AI right now. Please try again later."
    
    except requests.RequestException as e:
        # Log and return an error message in case of a request failure
        print(f"Error contacting Kora AI API: {e}")
        return "⚠️ Oops! Something went wrong. Please try again later."

def format_ai_reply(ai_reply):
    """
    Formats the AI's response to be more visually appealing.
    """
    return (
        "🧠 **Kora AI Response** 🧠\n\n"
        f"💬 **Response:**\n{ai_reply}\n\n"
        "✨ **Need more help?** Just ask me again with `/ai (your query)`! 😊"
    )
