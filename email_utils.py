import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


def send_email(to_email: str, subject: str, body: str) -> dict:
    """Send a simple email using SMTP. SMTP configuration is read from environment vars:
    SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, EMAIL_FROM
    Returns dict with status and message.
    """
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "0"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    email_from = os.getenv("EMAIL_FROM", user)

    if not host or not port or not user or not password:
        return {"status": "Failed", "message": "SMTP configuration missing in environment"}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = email_from
    msg["To"] = to_email
    msg.set_content(body)

    try:
        # Use SSL if port is 465, otherwise try STARTTLS on 587
        if port == 465:
            with smtplib.SMTP_SSL(host, port) as smtp:
                smtp.login(user, password)
                smtp.send_message(msg)
        else:
            with smtplib.SMTP(host, port) as smtp:
                smtp.ehlo()
                smtp.starttls()
                smtp.login(user, password)
                smtp.send_message(msg)
    except Exception as e:
        return {"status": "Failed", "message": str(e)}

    return {"status": "Sent", "message": f"Email sent to {to_email}"}
