import logging
import re
import time
from urllib.parse import parse_qs, urlparse

import aiohttp

logger = logging.getLogger(__name__)


def parse_redirect_url(query_string: str) -> dict[str, str]:
    """
    Parses a query string into a dictionary.

    Arguments:
        query_string (str): The query string from the URL.

    Returns:
        dict: A dictionary with query parameters as keys and their values as strings.
    """
    parsed_query = parse_qs(query_string)
    return {key: value[0] for key, value in parsed_query.items() if value}


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
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(url, timeout=timeout, ssl=False) as response:
                response_time = (time.time() - start_time) * 1000
                if response.status == 200:
                    return round(response_time)
    except aiohttp.ClientError as e:
        logger.warning(f"Failed to ping {url}: {str(e)}")
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
        parsed = urlparse(data)
        if all([parsed.scheme, parsed.netloc]):
            return True

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
