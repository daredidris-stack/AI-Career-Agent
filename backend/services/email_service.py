import logging
import smtplib
from email.message import EmailMessage

import requests

from backend.core.settings import (
    BREVO_API_KEY,
    BREVO_API_URL,
    EMAIL_FROM_NAME,
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
        return bool(SMTP_FROM_EMAIL and (BREVO_API_KEY or SMTP_HOST))

    def send(
        self,
        recipient: str,
        subject: str,
        body: str,
        headers: dict[str, str] | None = None,
    ) -> bool:
        if not self.configured:
            return False

        safe_headers = {
            name: value
            for name, value in (headers or {}).items()
            if name.casefold() == "list-unsubscribe"
            and "\r" not in value
            and "\n" not in value
        }

        if BREVO_API_KEY:
            return self._send_with_brevo(
                recipient,
                subject,
                body,
                safe_headers,
            )

        return self._send_with_smtp(
            recipient,
            subject,
            body,
            safe_headers,
        )

    def _send_with_brevo(
        self,
        recipient: str,
        subject: str,
        body: str,
        headers: dict[str, str],
    ) -> bool:
        payload: dict[str, object] = {
            "sender": {
                "name": EMAIL_FROM_NAME,
                "email": SMTP_FROM_EMAIL,
            },
            "to": [{"email": recipient}],
            "subject": subject,
            "textContent": body,
        }
        if headers:
            payload["headers"] = headers

        try:
            response = requests.post(
                BREVO_API_URL,
                headers={
                    "accept": "application/json",
                    "api-key": BREVO_API_KEY,
                    "content-type": "application/json",
                },
                json=payload,
                timeout=15,
            )
            response.raise_for_status()
            return True
        except requests.RequestException:
            logging.getLogger(__name__).exception(
                "Account email delivery failed"
            )
            return False

    def _send_with_smtp(
        self,
        recipient: str,
        subject: str,
        body: str,
        headers: dict[str, str],
    ) -> bool:
        message = EmailMessage()
        message["From"] = SMTP_FROM_EMAIL
        message["To"] = recipient
        message["Subject"] = subject
        for name, value in headers.items():
            message[name] = value
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
