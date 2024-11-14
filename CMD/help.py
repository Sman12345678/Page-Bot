import os
import importlib
import logging

# Configure logging
logger = logging.getLogger()

def execute():
    response = "📜 **KORA AI Command List** 📜\n\n"
    response += "Here are the available commands:\n\n"

    # Header for the command diagram
    response += "╔════════════════════════════╗\n"
    response += "║    📂 **Command Overview** 📂   ║\n"
    response += "╚════════════════════════════╝\n\n"

    # Iterate over each file in the CMD folder
    for filename in os.listdir("CMD"):
        if filename.endswith(".py") and filename != "__init__.py":
            command_name = filename[:-3]  # Remove .py extension

            # Dynamically load each command module
            try:
                cmd_module = importlib.import_module(f"CMD.{command_name}")
                # Try to get the Info dictionary for each command
                description = getattr(cmd_module, "Info", {}).get("Description", "No description available.")
                
                # Append each command in a structured format with emojis
                response += f"📌 **/{command_name}**\n"
                response += f"   📖 *Description*: {description}\n"
                response += "   ─────────────────────────────\n"

            except Exception as e:
                logger.warning(f"Failed to load command {command_name}: {e}")
                response += f"📌 **/{command_name}**\n"
                response += f"   📖 *Description*: Unable to load description.\n"
                response += "   ─────────────────────────────\n"

    # Footer with some extra info or design
    response += "\n🛠️ **Tip**: Use `/command_name` to activate a command.\n"
    response += "💡 **For Example**: Type `/up` to check bot's status.\n"
    response += "THANKS FOR USING 😁\n"
    response += "🛡️ KOLAWOLE SULEIMAN\n"

    return response
