import os
import time
import random
import requests
from datetime import datetime
import app
import messageHandler  # Make sure this import matches your project structure

PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")  # Set your Page's numeric ID as an environment variable

def post_text_to_page(message):
    """
    Posts text to the Facebook Page tied to PAGE_ACCESS_TOKEN via the /me/feed endpoint.
    """
    url = "https://graph.facebook.com/v22.0/me/feed"
    payload = {
        "message": message,
        "access_token": PAGE_ACCESS_TOKEN
    }
    return requests.post(url, data=payload).json()

def comment_on_post(post_id, comment_text):
    """
    Adds a comment or reply to a Facebook post or comment using the Graph API.
    """
    url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
    payload = {
        "message": comment_text,
        "access_token": PAGE_ACCESS_TOKEN
    }
    return requests.post(url, data=payload).json()

def get_content_pool():
    return [
        # --- Motivation & Quotes ---
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
        "💪 'Push yourself because no one else is going to do it for you.'",
        "🌟 'Great things never come from comfort zones.'",
        "🔥 'Don’t stop when you’re tired. Stop when you’re done.'",
        "🚀 'Success is not for the lazy.'",
        "✨ 'Wake up with determination, go to bed with satisfaction.'",
        "🎯 'It always seems impossible until it’s done.' – Nelson Mandela",
        "📈 'You don’t have to be great to start, but you have to start to be great.'",
        "⚡ 'Believe you can and you’re halfway there.' – Theodore Roosevelt",
        "💡 'Hard work beats talent when talent doesn’t work hard.'",
        "🌍 'The only limit to our realization of tomorrow is our doubts of today.' – FDR",
        "🤗 Your only limit is your mind.",
        "💫 Start where you are. Use what you have. Do what you can.",
        "🏆 Winners are not afraid of losing. But losers are.",
        "💭 Turn your dreams into plans.",
        "⏳ It’s never too late to be what you might have been.",
        "🚦 Don’t wait for opportunity. Create it.",
        "🥇 Every accomplishment starts with the decision to try.",
        "🪄 Magic is believing in yourself.",
        "🧗‍♂️ Difficult roads often lead to beautiful destinations.",
        "🌤️ Keep going. Everything you need will come to you at the right time.",
        # --- Tech Tips ---
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
        "🧑‍💻 Automate repetitive tasks with scripts or tools.",
        "📲 Review app permissions after every update.",
        "✨ Use two-factor authentication for extra security.",
        "🛡️ Regularly scan your devices for malware.",
        "🔋 Use dark mode to save battery on OLED screens.",
        # --- AI Facts ---
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
        "📷 AI powers facial recognition in modern smartphones.",
        "🎼 AI can compose music in the style of any artist.",
        "🌎 AI is used for climate change modeling and prediction.",
        "🛰️ AI helps satellites process images faster.",
        # --- DIY & Life Tips ---
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
        "🌞 Get sunlight daily for vitamin D and better mood.",
        "🧴 Use coconut oil as a natural moisturizer.",
        "🧤 Wear gloves when cleaning to protect your hands.",
        "🧺 Sort laundry by color and fabric for best results.",
        "💤 Good sleep is the foundation of productivity.",
        # --- Productivity & Mindset ---
        "🗂️ Break big goals into smaller tasks.",
        "⏰ Use the Pomodoro technique for focused work.",
        "📋 Make a to-do list every morning.",
        "📵 Turn off notifications during deep work.",
        "🛑 Learn to say no to avoid burnout.",
        "🚶‍♂️ Take a walk to clear your mind.",
        "🎧 Listen to music that helps you focus.",
        "⏱️ Time block your calendar for important tasks.",
        "🥤 Stay hydrated for better concentration.",
        "🤝 Collaboration multiplies results."
    ]

def get_all_posts(limit=20):
    """
    Returns a list of your Page's most recent posts.
    """
    url = f"https://graph.facebook.com/v22.0/{PAGE_ID}/feed"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "limit": limit
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])

def get_comments_for_post(post_id, limit=30):
    """
    Returns a list of comments for a given post.
    """
    url = f"https://graph.facebook.com/v22.0/{post_id}/comments"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "id,from,message,parent",
        "limit": limit
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])

def has_bot_replied(comment_id):
    """
    Checks if the bot (your Page) has already replied to this comment.
    """
    url = f"https://graph.facebook.com/v22.0/{comment_id}/comments"
    params = {
        "access_token": PAGE_ACCESS_TOKEN,
        "fields": "from"
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    replies = r.json().get("data", [])
    for reply in replies:
        if reply.get("from", {}).get("id") == PAGE_ID:
            return True
    return False

def auto_reply_comments():
    """
    Scans recent posts and replies to new user comments using messageHandler.handle_text_message().
    """
    posts = get_all_posts()
    for post in posts:
        post_id = post["id"]
        comments = get_comments_for_post(post_id)
        for comment in comments:
            comment_id = comment["id"]
            user_id = comment.get("from", {}).get("id")
            comment_text = comment.get("message")
            # Only reply to user comments, not to the bot's own or replies
            if user_id and user_id != PAGE_ID and not has_bot_replied(comment_id):
                # You can use get_conversation_history here if needed
                history = []
                try:
                    reply_text = messageHandler.handle_text_message(user_id, comment_text, history)
                    result = comment_on_post(comment_id, reply_text)
                    print(f"[{datetime.now()}] 💬 Auto-replied to comment {comment_id}: {result}")
                except Exception as e:
                    print(f"[{datetime.now()}] ❌ Failed to auto-reply to comment {comment_id}: {e}")
            else:
                print(f"[{datetime.now()}] ⏩ Skipped comment {comment_id}")

def post():
    """
    Posts a random message from the content pool every 24 hours and auto-replies to comments.
    """
    while True:
        message = random.choice(get_content_pool())
        try:
            result = post_text_to_page(message)
            if result.get("error", {}).get("code") == 100:
                app.report(f"Autopost OAuthException, need app-scoped ID: {result['error']['message']}")
            print(f"[{datetime.now()}] ✅ Auto-posted: {message}")
            print(f"📡 Facebook Response: {result}")

            post_id = result.get("id")
            if post_id:
                comment_text = "🤖 This is an automatic reply. Thanks for engaging with our post!"
                comment_result = comment_on_post(post_id, comment_text)
                print(f"[{datetime.now()}] 💬 Auto-commented: {comment_result}")
            else:
                print(f"[{datetime.now()}] ⚠️ No post ID returned; auto-comment skipped.")

        except Exception as e:
            print(f"[{datetime.now()}] ❌ Auto-post failed: {e}")
            app.report(f"Autopost error: {e}")

        # After posting, also scan for new comments to reply to
        auto_reply_comments()
        time.sleep(86400)  # wait 24 hours

