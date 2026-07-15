import os

import httpx


def send_email(to: str, subject: str, body: str) -> None:
    api_key = os.getenv("MJ_APIKEY_PUBLIC", "").strip()
    api_secret = os.getenv("MJ_APIKEY_PRIVATE", "").strip()
    from_email = os.getenv("GMAIL_ADDRESS", "").strip()

    if not api_key or not api_secret or not from_email:
        print(
            f"\n[DEV MODE — EMAIL NOT SENT] To: {to} | Subject: {subject}\n{body}\n"
        )
        return

    try:
        response = httpx.post(
            "https://api.mailjet.com/v3.1/send",
            auth=(api_key, api_secret),
            json={
                "Messages": [
                    {
                        "From": {"Email": from_email},
                        "To": [{"Email": to}],
                        "Subject": subject,
                        "TextPart": body,
                    }
                ]
            },
        )
        if response.status_code >= 300:
            print(
                f"\n[EMAIL FAILED] Status: {response.status_code} | To: {to} | Subject: {subject}\n{body}\n"
            )
    except Exception:
        print(
            f"\n[EMAIL FAILED — EXCEPTION] To: {to} | Subject: {subject}\n{body}\n"
        )
