import time
import calendar
Info = {
    "Description":"Time and Date. Depending on your time Zone"
}

def execute():
    # Get the current time and date information
    localtime = time.localtime(time.time())
    period = time.asctime(localtime)
    cal = calendar.month(localtime.tm_year, localtime.tm_mon)
    
    # Extract relevant parts of the local time
    year, month, day, hour, minute = localtime[0:5]
    
    # Format the output
    response = (
        "________________________\n"
        "|                       |\n"
        "| Today's Date 🌍       |\n"
        "|_______________________|\n"
        f"⏰ Time      | {hour:02d}:{minute:02d}\n"
        f"🗺️ Date      | {month}/{day}/{year}\n"
        "|                       |\n"
        "|_______ Calendar 📜 ___|\n"
        f"{cal}\n"
        "|_______________________|\n"
        f"| {period[:11]}\n"
        "________________________"
    )
    
    return response
