import os
import logging

Info = {
    "Description": "Admin-only: View the code of a CMD file. Usage: /file filename.py"
}

def execute(message, sender_id):
    ADMIN_ID = os.getenv("ADMIN_ID")
    if str(sender_id) != str(ADMIN_ID):
        return {"success": False, "type": "text", "data": "🚫 Only the admin can use this command."}
    try:
        filename = message.strip()
        if not filename.endswith(".py") or "/" in filename or "\\" in filename:
            return {"success": False, "type": "text", "data": "❌ Invalid filename."}
        file_path = os.path.join("CMD", filename)
        if not os.path.exists(file_path):
            return {"success": False, "type": "text", "data": f"❌ File CMD/{filename} does not exist."}
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        # Truncate if too long for Messenger (limit to ~2000 chars)
        if len(code) > 1800:
            code = code[:1800] + "\\n... (truncated)"
        return {"success": True, "type": "text", "data": f"📄 CMD/{filename} code:\\n\\n{code}"}
    except Exception as e:
        logging.error(f"File command error: {e}")
        return {"success": False, "type": "text", "data": f"🚨 Error reading file: {e}"}
