import os
import logging

Info = {
    "Description": "Admin-only: View the code of any file in your project. Usage: /file filename_or_path"
}

def execute(message, sender_id):
    ADMIN_ID = os.getenv("ADMIN_ID")
    if str(sender_id) != str(ADMIN_ID):
        return {"success": False, "type": "text", "data": "🚫 Only the admin can use this command."}
    try:
        filename = message.strip()
        # Disallow directory traversal and absolute paths
        if ".." in filename or filename.startswith("/") or "\\" in filename:
            return {"success": False, "type": "text", "data": "❌ Invalid filename or path."}
        file_path = os.path.join(os.getcwd(), filename)
        if not os.path.isfile(file_path):
            return {"success": False, "type": "text", "data": f"❌ File {filename} does not exist."}
        with open(file_path, "r", encoding="utf-8") as f:
            code = f.read()
        if len(code) > 1800:
            code = code[:1800] + "\n... (truncated)"
        return {"success": True, "type": "text", "data": f"📄 {filename} code:\n\n{code}"}
    except Exception as e:
        logging.error(f"File command error: {e}")
        return {"success": False, "type": "text", "data": f"🚨 Error reading file: {e}"}
