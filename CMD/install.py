import os
import logging

Info = {
    "Description": "Admin-only: Install (create/update) a CMD file. Usage: /install filename.py\\n<code>"
}

def execute(message, sender_id):
    ADMIN_ID = os.getenv("ADMIN_ID")
    if str(sender_id) != str(ADMIN_ID):
        return {"success": False, "type": "text", "data": "🚫 Only the admin can use this command."}
    
    try:
        # Expecting message of the form: filename.py\\n<code>
        if not message or ".py" not in message or "\\n" not in message:
            return {"success": False, "type": "text", "data": "❌ Invalid format. Usage: /install filename.py\\n<code>"}
        
        filename, code = message.split("\\n", 1)
        filename = filename.strip()
        # Sanitize filename
        if not filename.endswith(".py") or "/" in filename or "\\" in filename:
            return {"success": False, "type": "text", "data": "❌ Invalid filename."}
        file_path = os.path.join("CMD", filename)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code.strip())
        return {"success": True, "type": "text", "data": f"✅ CMD/{filename} installed successfully."}
    except Exception as e:
        logging.error(f"Install error: {e}")
        return {"success": False, "type": "text", "data": f"🚨 Error installing file: {e}"}
