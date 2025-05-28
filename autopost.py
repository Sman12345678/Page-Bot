import os
import time
import random
import requests
from datetime import datetime
from app import report

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

def post_text_to_page(message):
    url = f"https://graph.facebook.com/{PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, data=payload)
    return response.json()

def get_content_pool():
    return [
        # Motivation & Quotes
        "🌟 Believe in yourself. You're stronger than you think.",
        "🔥 Every small step counts — keep moving forward.",
        "🧠 'The best way to get started is to quit talking and begin doing.' – Walt Disney",
        "💬 'Success is not in what you have, but who you are.' – Bo Bennett",
        "🌱 'Do something today that your future self will thank you for.'",
        "🚀 'Don't watch the clock; do what it does. Keep going.' – Sam Levenson",
        "💡 'Success usually comes to those who are too busy to be looking for it.'",
        "🎯 'You miss 100% of the shots you don't take.' – Wayne Gretzky",
        "📚 'The harder you work for something, the greater you'll feel when you achieve it.'",
        "🌞 'Dream it. Wish it. Do it.'",
        "💪 ‘Push yourself because no one else is going to do it for you.’",
        "🌟 ‘Great things never come from comfort zones.’",
        "🔥 ‘Don’t stop when you’re tired. Stop when you’re done.’",
        "🚀 ‘Success is not for the lazy.’",
        "✨ ‘Wake up with determination, go to bed with satisfaction.’",
        "🎯 ‘It always seems impossible until it’s done.’ – Nelson Mandela",
        "📈 ‘You don’t have to be great to start, but you have to start to be great.’",
        "⚡ ‘Believe you can and you’re halfway there.’ – Theodore Roosevelt",
        "💡 ‘Hard work beats talent when talent doesn’t work hard.’",
        "🌍 ‘The only limit to our realization of tomorrow is our doubts of today.’ – FDR",
        # Tech Tips
        "🔐 Always use strong, unique passwords for every account.",
        "💡 Keep your software updated to protect against vulnerabilities.",
        "📱 Use app permissions wisely to protect your privacy.",
        "🛠️ Backup your important data regularly.",
        "💾 Cloud storage is great for sharing and backup.",
        "🔍 Use keyboard shortcuts to speed up your work.",
        "⚡ Turn off unused devices to save energy and battery life.",
        "🧹 Clear your browser cache periodically for better performance.",
        "💻 Learn one new programming concept every week.",
        "🌐 Use HTTPS websites for safer browsing.",
        "🖥️ Practice coding challenges daily to improve problem-solving skills.",
        "📡 Subscribe to tech newsletters to stay updated.",
        "🔧 Keep your device drivers updated for smooth operation.",
        "🖱️ Customize shortcuts and macros to boost productivity.",
        "🔒 Use VPNs on public Wi-Fi to protect your data.",
        # AI Facts
        "🤖 GPT models learn patterns from massive datasets of text.",
        "🧠 AI is helping doctors diagnose diseases earlier.",
        "📊 Machine learning models improve with more data.",
        "🤖 Natural Language Processing lets machines understand human language.",
        "🚗 Self-driving cars rely heavily on AI and sensors.",
        "🎨 AI can now generate art, music, and even write stories.",
        "📈 AI helps businesses predict customer trends.",
        "👾 AI chatbots improve customer service availability.",
        "🧬 AI is accelerating research in genetics and biology.",
        "🔮 The future of AI includes personalized assistants and smart homes.",
        "⚙️ Understanding AI ethics is key to responsible development.",
        "🔍 AI improves search engines by better understanding queries.",
        "🎯 AI models require constant updates to stay relevant.",
        # DIY & Life Tips
        "🧰 DIY Tip: Baking soda + vinegar is a natural cleaner.",
        "🔧 Fix squeaky hinges with a little WD-40 or cooking oil.",
        "📦 Organize cables using old bread clips as labels.",
        "🧴 Use lemon juice to remove stains and brighten whites.",
        "📅 Plan your day the night before to boost productivity.",
        "💧 Drink enough water every day for better health.",
        "🧘 Take short breaks during work to refresh your mind.",
        "🍳 Cooking tip: Let meat rest before cutting for juicier results.",
        "🛏️ Make your bed daily to start the day with accomplishment.",
        "📖 Read a little each day to expand your knowledge.",
        "🌿 Houseplants improve air quality and mood.",
        "⚡ Unplug electronics not in use to save energy.",
        "🛠️ Regularly check and maintain home safety devices.",
        "🎨 Try a new hobby to boost creativity and reduce stress.",
        "🌞 Get sunlight daily for vitamin D and better mood."
    ]

def post():
    while True:
        try:
            message = random.choice(get_content_pool())
            result = post_text_to_page(message)
            print(f"[{datetime.now()}] ✅ Auto-posted: {message}")
            print(f"📡 Facebook Response: {result}")
        except Exception as e:
            print(f"[{datetime.now()}] ❌ Auto-post failed: {e}")
            report(f"Autopost error:{e}")

        time.sleep(86400)  # sleep 24 hours
