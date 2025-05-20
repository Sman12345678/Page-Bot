import os

Info = {
    "Description": "Admin-only: The command is restricted to admin usage"
}

def execute(message=None, sender_id):
    ADMIN_ID = os.getenv("ADMIN_ID")
    if str(sender_id) != str(ADMIN_ID):
        return {
            "success": False,
            "type": "text",
            "data": "🚫 This room is for the Bot owner only."
        }
    # List of admin-only commands
    admin_cmds = [
        "/admin   - Show this admin panel",
        "/install - Install a CMD file from code",
        "/file    - View the code of a CMD file",
        # Add more admin commands here as needed
    ]
    return {
        "success": True,
        "type": "text",
        "data": (
            "👑 Welcome, Admin!\n"
            "This is your special command room.\n\n"
            "🛠️ **Admin Commands:**\n"
            + "\n".join(admin_cmds) +
            "\n\nFeel free to use your powers responsibly! 💪"
        )
    }
