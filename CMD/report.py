import app as Suleiman
import os
user_id = os.getenv("ADMIN_ID")

def execute(message,sender_id):
    if not message:
        return "🧘 Please provide a message to be sent to Admin"
    
    # Send the message to the admin
    success = Suleiman.send_message(
        user_id,
        f"""📩 |== Quick Message ==|

👨‍💻 Message From:{sender_id}

📝 |== Body ==|  
{message}  

📬 |==========|"""
    )
    if success:
        return "✅ Your message has been sent to the admin successfully!"
    else:
        return "⚠️ Failed to send your message to the admin. Please try again later."
