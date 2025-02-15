import time
from urllib.parse import parse_qs

import aiohttp


def parse_redirect_url(query_string: str) -> dict[str, str]:
    return {key: value[0] for key, value in parse_qs(query_string).items() if value}


async def ping_url(url: str, timeout: int = 5) -> float | None:
    async with aiohttp.ClientSession() as session:
        start_time = time.time()
        async with session.get(url=url, timeout=timeout, ssl=False) as response:
            if response.status == 200:
                return round((time.time() - start_time) * 1000)
    return None
