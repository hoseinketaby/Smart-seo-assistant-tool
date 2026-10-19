import base64
import os
from cryptography.fernet import Fernet

def _cipher():
    key = os.getenv("ENCRYPTION_KEY", "")
    if not key:
        raise RuntimeError("ENCRYPTION_KEY is required to protect API credentials.")
    return Fernet(key.encode("ascii"))

def encrypt_value(text: str) -> str:
    if not text:
        return ""
    return "fernet:" + _cipher().encrypt(text.encode("utf-8")).decode("ascii")

def decrypt_value(text: str) -> str:
    if not text:
        return ""
    if text.startswith("fernet:"):
        return _cipher().decrypt(text[len("fernet:"):].encode("ascii")).decode("utf-8")
    decoded = base64.urlsafe_b64decode(text.encode()).decode("utf-8")
    salt = os.getenv("ENCRYPTION_SALT", "my-app-salt")
    if not decoded.startswith(f"{salt}:"):
        raise ValueError("Invalid legacy API credential")
    return decoded[len(salt) + 1:]
