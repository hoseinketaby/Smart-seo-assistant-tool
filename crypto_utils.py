import base64
import os

SALT = os.getenv("ENCRYPTION_SALT", "my-app-salt")

def encrypt_value(text: str) -> str:
    if not text:
        return ""
    payload = f"{SALT}:{text}"
    return base64.urlsafe_b64encode(payload.encode()).decode()

def decrypt_value(text: str) -> str:
    if not text:
        return ""
    decoded = base64.urlsafe_b64decode(text.encode()).decode()
    if decoded.startswith(f"{SALT}:"):
        return decoded[len(SALT)+1:]
    return decoded
