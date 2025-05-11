import app as Suleiman

user_id = 8711876652167640

def execute(message):
    if not message:
        return "🧘 Please provide a message to be sent to Admin"
    
    # Send the message to the admin
    success = Suleiman.send_message(
        user_id,
        f"""📩 |== Quick Message ==|

👨‍💻 **Message From**: Bot User  

📝 |=== Body ===|  
{message}  

📬 |=============|"""
    )
    if success:
        return "✅ Your message has been sent to the admin successfully!"
    else:
        return "⚠️ Failed to send your message to the admin. Please try again later."
