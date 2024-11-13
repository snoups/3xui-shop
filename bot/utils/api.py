from py3xui import AsyncApi, Client

from bot.database import crud
from bot.database.models import User
from bot.utils.config import config
from bot.utils.logger import Logger

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


async def get_client_data(telegram_id: int) -> dict | None:
    """
    Fetches client data from the XUI API by user ID and prepares it for display.

    Args:
        user_id (int): The ID of the user for which to retrieve the client data.

    Returns:
        dict: A dictionary containing client data such as total traffic, uploaded/downloaded traffic, and expiry time.
    """
    try:
        client: Client = await api.client.get_by_email(telegram_id)

        if client is None:
            return None

        logger.debug(client.model_dump())

        remaining_traffic: int
        plan: int

        if client.total == 0:
            remaining_traffic = -1
            plan = -1
        else:
            remaining_traffic = client.total - (client.up + client.down)
            plan = client.total

        total = client.up + client.down
        up = client.up
        down = client.down
        expiry_time = client.expiry_time

        return {
            "plan": plan,
            "remaining_traffic": remaining_traffic,
            "expiry_time": expiry_time,
            "total": total,
            "up": up,
            "down": down,
        }
    except Exception as e:
        logger.error(f"Error fetching client data for user {telegram_id}: {e}")
        return {}


async def reset_traffic(telegram_id):
    client: Client = await api.client.get_by_email(telegram_id)
    await api.client.reset_stats(client.inbound_id, telegram_id)


async def add_client(telegram_id):
    user: User = crud.get_user(telegram_id)
    new_client = Client(id=user.id, email=str(telegram_id), enable=True)

    await api.client.add(6, [new_client])
    client = await api.client.get_by_email(telegram_id)

    logger.debug(client.model_dump())


async def set_traffic_limit() -> None:
    client = await api.client.get_by_email(str("tes2t"))
    client.id = "24d8083b-03bc-48c1-9668-bbd1063afb0a"
    client.total_gb = 1024
    await api.client.update("24d8083b-03bc-48c1-9668-bbd1063afb0a", client)
