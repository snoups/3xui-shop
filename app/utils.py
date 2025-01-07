import re
from urllib.parse import urlparse

import requests


async def ping_url(url: str, timeout: int = 5) -> float | None:
    """
    Ping a URL and return the response time in milliseconds.

    Arguments:
        url (str): The URL to ping.
        timeout (int): The maximum time to wait for a response, in seconds.

    Returns:
        float | None: The response time in milliseconds, or None if the request failed.
    """
    try:
        response = requests.get(url, timeout=timeout)
        if response.status_code == 200:
            return round(response.elapsed.total_seconds() * 1000)
    except requests.RequestException:
        return None


def is_valid_host(data: str) -> bool:
    """
    Validates if the given data is a valid URL or IP address.

    Arguments:
        data (str): The data to validate.

    Returns:
        bool: True if the data is a valid URL or IP, False otherwise.
    """
    try:
        # Check if it's a valid URL
        parsed = urlparse(data)
        if all([parsed.scheme, parsed.netloc]):
            return True
        # Check if it's a valid IP
        ip_pattern = re.compile(
            r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}"
            r"(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        )
        if ip_pattern.match(data):
            return True
    except Exception:
        return False

    return False


def is_valid_client_count(data: str) -> bool:
    """
    Validates if the given data is a valid client count (positive integer, minimum 1).

    Arguments:
        data (str): The data to validate.

    Returns:
        bool: True if the data is a valid client count (positive integer >= 1), False otherwise.
    """
    return data.isdigit() and int(data) >= 1
