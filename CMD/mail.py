import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Command Info
Info = {
    "Description": "Send an email using SMTP. Format: 'recipient_email, subject, body'"
}

def execute(message):
    """
    Send an email using SMTP based on the provided message.

    Args:
        message (str): Input in the format 'recipient_email, subject, body'.

    Returns:
        dict: Contains success status and a response message.
    """
    # SMTP Server Configuration
    SMTP_SERVER = "smtp.gmail.com"  # Replace with your SMTP server
    SMTP_PORT = 587  # Port for TLS
    SMTP_USERNAME = "quickmail487@gmail.com"  # Replace with your email
    SMTP_PASSWORD = "wuzt iurl zihx nvdn"  # Replace with your email password

    try:
        # Validate and parse the input message
        parts = message.split(",")
        if len(parts) < 3:
            return {"success": False, "data": "🚨 Invalid format. Use: 'recipient_email, subject, body'"}

        recipient_email = parts[0].strip()
        subject = parts[1].strip()
        body = ",".join(parts[2:]).strip()  # Handle cases where body contains commas

        # Create the email
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server and send the email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Upgrade the connection to a secure encrypted SSL/TLS connection
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, recipient_email, msg.as_string())
        server.quit()

        return {"success": True, "data": f"✅ Email sent successfully to {recipient_email}!"}

    except Exception as e:
        return {"success": False, "data": f"🚨 An error occurred: {str(e)}"}
