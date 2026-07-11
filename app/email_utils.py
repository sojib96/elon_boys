import os
import smtplib
from email.mime.text import MIMEText


def send_email(to: str, subject: str, body: str) -> None:
    gmail_address = os.getenv("GMAIL_ADDRESS", "").strip()
    gmail_password = os.getenv("GMAIL_APP_PASSWORD", "").strip()

    if not gmail_address or not gmail_password:
        print(
            f"\n[DEV MODE — EMAIL NOT SENT] To: {to} | Subject: {subject}\n{body}\n"
        )
        return

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = gmail_address
    msg["To"] = to

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail_address, gmail_password)
        server.send_message(msg)
