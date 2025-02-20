import app as Suleiman

user_id = 8711876652167640

def execute(message):
    if not message:
        return "🧘 Please provide a message to be sent to Admin"

    response = Suleiman.send_message(user_id, 
        f"""📩 |==== Quick Message ====|

👨‍💻 **Message From**: A User  

📝 |==== Body ====|  
{message}  

📬 |================|"""
    )

    return response
