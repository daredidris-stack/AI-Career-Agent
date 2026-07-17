import smtplib
import logging
from email.message import EmailMessage

from backend.core.settings import (
    SMTP_FROM_EMAIL,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_USE_TLS,
)


class EmailService:
    @property
    def configured(self) -> bool:
        return bool(SMTP_HOST and SMTP_FROM_EMAIL)

    def send(self, recipient: str, subject: str, body: str) -> bool:
        if not self.configured:
            return False

        message = EmailMessage()
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)

        try:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=15) as server:
                if SMTP_USE_TLS:
                    server.starttls()
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
            return True
        except (OSError, smtplib.SMTPException):
            logging.getLogger(__name__).exception("Account email delivery failed")
            return False
