# command.py
import requests
import os 

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")

def register_commands():
    data = {
        "commands": [
            {
                "locale": "default",
                "commands": [
                    {"name": "help", "description": "Show help menu"},
                    {"name": "news", "description": "Get latest news"},
                    {"name": "quote", "description": "Get a random quote"},
                    {"name": "up", "description": "Show bot uptime"},
                    {"name": "bbc", "description": "Get BBC headlines"}
                ]
            }
        ]
    }

    res = requests.post(
        f"https://graph.facebook.com/v22.0/me/messenger_profile?access_token={PAGE_ACCESS_TOKEN}",
        json=data
    )

    print("Status:", res.status_code)
    print("Response:", res.json())
