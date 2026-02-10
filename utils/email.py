import smtplib
from email.message import EmailMessage
from config import Config
import traceback

def send_email_smtp(subject: str, to: str, body: str, html: str = None) -> bool:
    """Send email using SMTP settings from Config. Returns True on success."""
    if not Config.SMTP_SERVER or not Config.SMTP_USERNAME or not Config.SMTP_PASSWORD:
        # SMTP not configured
        return False

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = Config.EMAIL_SENDER
    msg['To'] = to
    msg.set_content(body)
    if html:
        msg.add_alternative(html, subtype='html')

    try:
        if Config.SMTP_USE_TLS:
            server = smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT, timeout=10)

        server.login(Config.SMTP_USERNAME, Config.SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception:
        traceback.print_exc()
        return False
