
import app as Suleiman

user_id = 8711876652167640  

def execute(message):
    if message is None: 
        return "🧘 Please provide a message to be sent to Admin"
    else:
        response = Suleiman.send_message(user_id, message)
        return response
