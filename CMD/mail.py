import smtplib
import os
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

# Command Info
Info = {
    "Description": "Send an email using SMTP. Format: 'recipient_email, subject, body'"
}

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def is_valid_email(email):
    """Check if the provided email is in a valid format."""
    regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(regex, email)

def execute(message=None):
    """
    Send an email using SMTP based on the provided message.

    Args:
        message (str): Input in the format 'recipient_email, subject, body'.

    Returns:
        dict: Contains success status and a response message.
    """
    # Check if no message is provided
    if not message:
        return {"success": False, "data": "🚨 No message provided. Format: 'recipient_email, subject, body'"}

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
        if not is_valid_email(recipient_email):
            return {"success": False, "data": "🚨 Invalid recipient email format."}

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

    except smtplib.SMTPAuthenticationError:
        logging.error("Authentication failed. Please check your email and password.")
        return {"success": False, "data": "🚨 Authentication failed. Please check your credentials."}
    except smtplib.SMTPConnectError:
        logging.error("Connection error while connecting to the SMTP server.")
        return {"success": False, "data": "🚨 Connection error. Please try again later."}
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        return {"success": False, "data": f"🚨 An unexpected error occurred: {str(e)}"} # R theeplace with your email
     
