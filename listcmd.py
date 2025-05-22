import requests
import os

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

def register_persistent_menu():
    menu_data = {
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {"type": "postback", "title": "Help", "payload": "/help"},
                    {"type": "postback", "title": "News", "payload": "/news"},
                    {"type": "postback", "title": "Quote", "payload": "/quote"},
                    {"type": "postback", "title": "Uptime", "payload": "/up"},
                    {"type": "postback", "title": "BBC Headlines", "payload": "/bbc"}
                ]
            }
        ]
    }

    res = requests.post(
        f"https://graph.facebook.com/v22.0/me/messenger_profile?access_token={PAGE_ACCESS_TOKEN}",
        json=menu_data
    )
    print("Status:", res.status_code)
    print("Response:", res.json())
