import app  # Import the main app to access `get_bot_uptime`

# Description dictionary
Info = {
    "Description": "KORA AI Bot Status",
    "bot_name": "KORA AI",
    "owner": "Kolawole Suleiman",
    "version": "v1.0",
    "purpose": "Provides assistance, information, and companionship.",
    "last_update": "September 14, 2024"
}

def format_duration(seconds):
    """
    Format time into a human-readable format: days, hours, minutes, and seconds.
    """
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    return f"{int(days)}d {int(hours)}h {int(minutes)}m {int(seconds)}s"

def execute():
    """
    Generate and return the bot's status report.
    """
    # Get the bot's uptime in seconds
    uptime_seconds = app.get_bot_uptime()

    # Format uptime for better readability
    uptime_str = format_duration(uptime_seconds)

    # Visual and structured response
    response = (
        "╭───────────────────────────╮\n"
        "│       🤖 KORA AI Status       │\n"
        "╰───────────────────────────╯\n\n"
        f"🔷 Bot Name: {Info['bot_name']}\n"
        f"👤 Owner: {Info['owner']}\n"
        f"📌 Version: {Info['version']}\n"
        f"🎯 Purpose: {Info['purpose']}\n"
        f"📅 Last Update: {Info['last_update']}\n\n"
        "⏳ Uptime:\n"
        f"   🕒 {uptime_str}\n\n"
        "╭───────────────────────────╮\n"
        "│ 🙏 Thank you for using KORA AI! │\n"
        "╰───────────────────────────╯\n"
    )

    return response
