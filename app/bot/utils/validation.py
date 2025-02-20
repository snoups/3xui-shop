import re
from urllib.parse import urlparse

IP_PATTERN = re.compile(
    r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}" r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
)


def is_valid_host(data: str) -> bool:
    parsed = urlparse(data)
    if all([parsed.scheme, parsed.netloc]):
        return True
    return bool(IP_PATTERN.match(data))


def is_valid_client_count(data: str) -> bool:
    return data.isdigit() and 1 <= int(data) <= 10000


def is_valid_user_id(data: str) -> bool:
    return data.isdigit() and 1 <= int(data) <= 1000000000000


def is_valid_message_text(data: str) -> bool:
    return len(data) <= 4096
