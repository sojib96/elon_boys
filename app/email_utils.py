import os

import httpx


def send_email(to: str, subject: str, body: str) -> bool:
    api_key = os.getenv("RESEND_API_KEY", "").strip()
    from_email = os.getenv("GMAIL_ADDRESS", "").strip()

    if not api_key or not from_email:
        print(
            f"\n[DEV MODE — EMAIL NOT SENT] To: {to} | Subject: {subject}\n{body}\n"
        )
        return False

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}"},
            json={
                "from": from_email,
                "to": [to],
                "subject": subject,
                "text": body,
            },
        )
        if response.status_code >= 300:
            print(
                f"\n[EMAIL FAILED] Status: {response.status_code} | {response.text}\n"
            )
            return False
        return True
    except Exception:
        print(
            f"\n[EMAIL FAILED — EXCEPTION] To: {to} | Subject: {subject}\n{body}\n"
        )
        return False
