import logging
from datetime import datetime, timedelta, timezone

from py3xui import AsyncApi, Client

from app.config import Config
from app.db.models.user import User

logger = logging.getLogger(__name__)


class VPNService:
    """
    Service for interacting with the 3XUI API to manage client data and subscriptions.

    This service provides methods to create, update, and retrieve client information, as well as
    check if a client exists. It interacts with the 3XUI API to manage VPN clients and their data.

    Attributes:
        api (AsyncApi): An instance of the AsyncApi to interact with the 3XUI API.
    """

    def __init__(self, config: Config) -> None:
        """
        Initializes the VPNService object with the given configuration.

        Arguments:
            config (Config): Configuration object containing the necessary credentials and settings
                             to authenticate and interact with the 3XUI API.
        """
        self.api = AsyncApi(
            host=config.xui.HOST,
            username=config.xui.USERNAME,
            password=config.xui.PASSWORD,
            token=config.xui.TOKEN,
            use_tls_verify=False,
            logger=logging.getLogger("xui"),
        )

    async def initialize(self) -> None:
        """
        Logs into the 3XUI API using the provided credentials.

        This method must be called before performing any actions with the API, as it authenticates
        the session and prepares the service for interactions with the API.
        """
        await self.api.login()

    async def is_client_exists(self, user_id: int) -> Client | None:
        """
        Checks if a client exists in the 3XUI by their user ID.

        Arguments:
            user_id (int): The user ID to check for existence.

        Returns:
            Client | None: The client object if found, otherwise None.
        """
        return await self.api.client.get_by_email(str(user_id))

    async def get_client_data(self, user_id: int) -> dict | None:
        """
        Retrieves detailed data for a client based on the user ID.

        Arguments:
            user_id (int): The user ID of the client whose data is to be retrieved.

        Returns:
            dict | None: A dictionary containing the client’s traffic and subscription data.
                         If an error occurs or client is not found, an empty dictionary is returned.
                         Traffic values are in bytes (`-1` unlimited traffic or subscription).
        """
        try:
            client: Client = await self.api.client.get_by_email(str(user_id))

            if client is None:
                return None

            traffic_total = client.total
            if traffic_total <= 0:
                traffic_remaining = -1
                traffic_total = -1
            else:
                traffic_remaining = client.total - (client.up + client.down)

            expiry_time = -1 if client.expiry_time == 0 else client.expiry_time

            traffic_used = client.up + client.down

            return {
                "traffic_total": traffic_total,
                "traffic_remaining": traffic_remaining,
                "traffic_used": traffic_used,
                "traffic_up": client.up,
                "traffic_down": client.down,
                "expiry_time": expiry_time,
            }
        except Exception as e:
            logger.error(f"Error retrieving client data: {e}")
            return {}

    async def update_client(self, user: User, traffic: int, duration: int) -> None:
        """
        Updates the client’s traffic and subscription duration in the 3XUI.

        Arguments:
            user (User): The user whose client data is to be updated.
            traffic (int): The traffic limit in GB to set for the client.
            duration (int): The duration in days for which the subscription is valid.
        """
        client: Client = await self.api.client.get_by_email(str(user.user_id))
        client.id = user.vpn_id
        client.expiry_time = self.days_to_unix_milliseconds(duration)
        client.flow = "xtls-rprx-vision"
        client.limit_ip = 3
        client.sub_id = str(user.user_id)
        client.total_gb = self.gb_to_bytes(traffic)

        await self.api.client.update(client.id, client)
        await self.api.client.reset_stats(client.inbound_id, client.email)

    async def create_client(self, user: User, traffic: int, duration: int) -> None:
        """
        Creates a new client in the 3XUI.

        Arguments:
            user (User): The user for whom the client is to be created.
            traffic (int): The traffic limit in GB to set for the new client.
            duration (int): The duration in days for which the subscription is valid.
        """
        new_client = Client(
            email=str(user.user_id),
            enable=True,
            id=user.vpn_id,
            expiryTime=self.days_to_unix_milliseconds(duration),
            flow="xtls-rprx-vision",
            limitIp=3,
            sub_id=str(user.user_id),
            totalGB=self.gb_to_bytes(traffic),
        )
        inbound_id = 7  # TODO: inbound id selection
        await self.api.client.add(inbound_id, [new_client])

    def gb_to_bytes(self, traffic_gb: int) -> int:
        """
        Convert traffic volume from gigabytes (GB) to bytes.

        Arguments:
            traffic_gb (int): The traffic volume in gigabytes.

        Returns:
            int: The traffic volume in bytes.
        """
        bytes_in_gb = 1024**3  # 1 GB = 1024^3 bytes
        return int(traffic_gb * bytes_in_gb)

    def days_to_unix_milliseconds(self, days: int) -> int:
        """
        Convert a number of days to a Unix timestamp in milliseconds.

        Arguments:
            days (int): Number of days to convert.

        Returns:
            int: Unix timestamp in milliseconds.
        """
        now = datetime.now(timezone.utc)
        target_time = now + timedelta(days=days)
        unix_timestamp_seconds = int(target_time.timestamp())
        unix_timestamp_milliseconds = unix_timestamp_seconds * 1000
        return unix_timestamp_milliseconds
