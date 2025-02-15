import uuid


def split_text(text: str, chunk_size: int = 4096) -> list[str]:
    """Split text into chunks of a given size."""
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def generate_code() -> str:
    """Generate an 8-character alphanumeric promocode."""
    code = str(uuid.uuid4()).replace("-", "").upper()[:8]
    return code
