import logging
import re
import time
import uuid
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import aiohttp

logger = logging.getLogger(__name__)


def parse_redirect_url(query_string: str) -> dict[str, str]:
    parsed_query = parse_qs(query_string)
    return {key: value[0] for key, value in parsed_query.items() if value}


async def ping_url(url: str, timeout: int = 5) -> float | None:
    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(url, timeout=timeout, ssl=False) as response:
                response_time = (time.time() - start_time) * 1000
                if response.status == 200:
                    return round(response_time)
    except aiohttp.ClientError as exception:
        logger.warning(f"Failed to ping {url}: {str(exception)}")
        return None


def is_valid_host(data: str) -> bool:
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
    return data.isdigit() and 1 <= int(data) <= 10000


def split_text(text: str, chunk_size: int = 4096) -> list[str]:
    return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]


def get_current_timestamp() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def add_days_to_timestamp(timestamp: int, days: int) -> int:
    current_datetime = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
    new_datetime = current_datetime + timedelta(days=days)
    return int(new_datetime.timestamp() * 1000)


def days_to_timestamp(days: int) -> int:
    current_time = get_current_timestamp()
    return add_days_to_timestamp(current_time, days)


def generate_code() -> str:
    code = str(uuid.uuid4()).replace("-", "").upper()[:8]
    logger.debug(f"Generated promocode: {code}")
    return code
