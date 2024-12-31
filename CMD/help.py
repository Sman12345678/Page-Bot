import os
import importlib
import logging

# Configure logging
logger = logging.getLogger()

def execute(message=None):
    # Start the response with a header and an updated diagram
    response = (
        "📜 **KORA AI Command List** 📜\n\n"
        "Here are the available commands:\n\n"
        "╭───────────────────╮\n"
        "│   📂 Command Overview  │\n"
        "╰───────────────────╯\n\n"
    )

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
                response += (
                    f"📌 **/{command_name}**\n"
                    f"   📖 *Description*: {description}\n"
                    f"   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
                )

            except Exception as e:
                logger.warning(f"Failed to load command {command_name}: {e}")
                response += (
                    f"📌 **/{command_name}**\n"
                    f"   ⚠️ *Description*: Unable to load description.\n"
                    f"   ~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
                )

    # Footer with some extra info or design
    response += (
        "\n💡 **How to Use Commands:**\n"
        "   - Type `/command_name` to use a command.\n"
        "   - Example: `/up` to check the bot's status.\n\n"
        "⚡ **Thanks for using KORA AI!** ⚡\n"
        "   🛡️ Developed by Kolawole Suleiman\n"
    )

    return response
