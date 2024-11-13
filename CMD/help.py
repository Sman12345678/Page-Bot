import os

def execute():
    cmd_folder = "CMD"
    cmds = []

    # Check each file in the CMD folder
    for filename in os.listdir(cmd_folder):
        if filename.endswith(".py") and filename != "help.py":  # Exclude help.py itself
            cmd_name = filename[:-3]  # Remove the .py extension
            cmds.append(cmd_name)

    # If no commands are found
    if not cmds:
        return "⚠️ No commands found in the CMD folder."

    # Sort the commands alphabetically
    cmds.sort()

    # Format the response with emojis and structure
    response = "📜 **Available Commands** 📜\n\n"
    response += "\n".join([f"🔹 **/{cmd}** - Use this command to check{cmd.replace('_', ' ')}" for cmd in cmds])
    response += "\n\n🤖 _Type a command with the prefix to use it!_ 🤖, Example /quote"
    response += "\n\n THANKS FOR USING 😁"

    return response
