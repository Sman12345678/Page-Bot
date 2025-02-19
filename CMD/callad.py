import app as Suleiman

user_id = 8711876652167640  

def execute(message):
    if not message:  # More Pythonic way to check for None or empty string
        return Suleiman.send_message(user_id, "🧘 Please provide a message to be sent to Admin")

    response = Suleiman.send_message(user_id, 
        f"""📩 |====== Quick Message ======|

👨‍💻 **Message From**: `{user_id}`  

📜 |====== Body ======|  
{message}  

📬 |===================|"""
    )

    Suleiman.send_message(user_id, "✅ Message sent successfully")
    return response

