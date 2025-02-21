import secrets
import string
import uuid

CHARSET = string.ascii_uppercase + string.digits


def split_text(text: str, chunk_size: int = 4096) -> list[str]:
    """Split text into chunks of a given size."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def generate_code(length: int = 8) -> str:
    """Generate an 8-character alphanumeric promocode."""
    return "".join(secrets.choice(CHARSET) for _ in range(length))
