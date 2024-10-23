from py3xui import AsyncApi, Client

from utils.config import config
from utils.helpers import (
    calculate_remaining_traffic,
    convert_size,
    time_left_to_expiry,
)
from utils.logger import Logger

logger = Logger(__name__).get_logger()
logger_xui: Logger = Logger("xui").get_logger()

api = AsyncApi(
    host=config.xui.host,
    username=config.xui.username,
    password=config.xui.password,
    token=config.xui.token,
    use_tls_verify=False,
    logger=logger_xui,
)


async def get_client_data(user_id: int, lang: str) -> dict | None:
    """
    Fetches client data from the XUI API by user ID and prepares it for display.

    Args:
        user_id (int): The ID of the user for which to retrieve the client data.
        lang (str): The user's language code for localization purposes.

    Returns:
        dict: A dictionary containing client data such as total traffic, uploaded/downloaded traffic, and expiry time.
    """
    try:
        client: Client = await api.client.get_by_email(user_id)

        if client is None:
            return None

        logger.debug(client.model_dump())

        remaining_traffic: str
        plan: str

        if client.total == 0:
            remaining_traffic = "∞"
            plan = "∞"
        else:
            remaining_traffic = calculate_remaining_traffic(
                client.up + client.down,
                client.total,
                lang,
            )
            plan = convert_size(client.total, lang)

        total = convert_size(client.up + client.down, lang)
        up = convert_size(client.up, lang)
        down = convert_size(client.down, lang)
        expiry_time = time_left_to_expiry(client.expiry_time, lang)

        return {
            "plan": plan,
            "remaining_traffic": remaining_traffic,
            "expiry_time": expiry_time,
            "total": total,
            "up": up,
            "down": down,
        }
    except Exception as e:
        logger.error(f"Error fetching client data for user {user_id}: {e}")
        return {}


async def reset_traffic(user_id):
    client: Client = await api.client.get_by_email(user_id)
    await api.client.reset_stats(client.inbound_id, user_id)
