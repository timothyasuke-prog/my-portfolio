import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = "super-secret-key"
    DATABASE = os.path.join(BASE_DIR, "database", "portfolio.db")
    # Email / SMTP settings (use SendGrid/Mailgun SMTP credentials or your SMTP server)
    SMTP_SERVER = os.environ.get('SMTP_SERVER', '')
    SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
    SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
    SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
    SMTP_USE_TLS = os.environ.get('SMTP_USE_TLS', '1') == '1'
    EMAIL_SENDER = os.environ.get('EMAIL_SENDER', 'no-reply@example.com')
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', '')
    ENABLE_ADMIN_EMAIL_ALERTS = os.environ.get('ENABLE_ADMIN_EMAIL_ALERTS', '1') == '1'
