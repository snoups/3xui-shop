import logging
from datetime import datetime, timedelta, timezone

from py3xui import AsyncApi, Client, Inbound
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.services import PromocodeService
from app.bot.services.client import ClientData
from app.config import Config
from app.db.models import Promocode, User

logger = logging.getLogger(__name__)


class VPNService:
    """
    Service for managing VPN client operations, including client creation, updating, and
    subscription management.

    Attributes:
        session (AsyncSession): Database session for operations.
        subscription (str): VPN subscription identifier.
        api (AsyncApi): API client for interacting with the VPN service.
        promocode_service (PromocodeService): Service for managing promocodes.
    """

    def __init__(
        self,
        session: AsyncSession,
        config: Config,
        promocode_service: PromocodeService,
    ) -> None:
        """
        Initializes the VPNService instance.

        Arguments:
            session (AsyncSession): The session for performing database operations.
            config (Config): Configuration containing VPN credentials and settings.
            promocode_service (PromocodeService): Service for managing promocodes.
        """
        self.session = session
        self.subscription = config.xui.SUBSCRIPTION
        self.api = AsyncApi(
            host=config.xui.HOST,
            username=config.xui.USERNAME,
            password=config.xui.PASSWORD,
            token=config.xui.TOKEN,
            use_tls_verify=False,
            logger=logging.getLogger("xui"),
        )
        self.promocode_service = promocode_service
        logger.info("VPNService initialized.")

    async def initialize(self) -> None:
        """
        Initializes the VPN service and logs in to the API.
        """
        await self.api.login()

    async def is_client_exists(self, user_id: int) -> Client | None:
        """
        Checks if a client exists by user ID.

        Arguments:
            user_id (int): The user ID to check.

        Returns:
            Client | None: The client if found, None otherwise.
        """
        client = await self.api.client.get_by_email(str(user_id))

        if client:
            logger.debug(f"Client {user_id} exists.")
        else:
            logger.debug(f"Client {user_id} not found.")

        return client

    async def get_limit_ip(self, client: Client) -> int | None:
        """
        Retrieves the IP limit for a specific client.

        Arguments:
            client (Client): The client to fetch the limit IP for.

        Returns:
            int | None: The IP limit for the client, or None if an error occurs.
        """
        try:
            inbounds: list[Inbound] = await self.api.inbound.get_list()
        except Exception as exception:
            logger.error(f"Failed to fetch inbounds: {exception}")
            return None

        for inbound in inbounds:
            for inbound_client in inbound.settings.clients:
                if inbound_client.email == client.email:
                    logger.debug(f"Client {client.email} limit ip: {inbound_client.limit_ip}")
                    return inbound_client.limit_ip

        logger.debug(f"Client {client.email} not found in inbounds.")
        return None

    async def get_client_data(self, user_id: int) -> ClientData | None:
        """
        Retrieves data for a specific client.

        Arguments:
            user_id (int): The user ID for which to retrieve client data.

        Returns:
            ClientData | None: The client data if found, or None if an error occurs.
        """
        logger.debug(f"Starting to retrieve client data for {user_id}.")
        try:
            client: Client = await self.api.client.get_by_email(str(user_id))

            if client is None:
                logger.debug(f"No client data found for {user_id}.")
                return None

            limit_ip = await self.get_limit_ip(client)
            max_devices = -1 if limit_ip == 0 else limit_ip
            traffic_total = client.total
            expiry_time = -1 if client.expiry_time == 0 else client.expiry_time

            if traffic_total <= 0:
                traffic_remaining = -1
                traffic_total = -1
            else:
                traffic_remaining = client.total - (client.up + client.down)

            traffic_used = client.up + client.down
            client_data = ClientData(
                max_devices=max_devices,
                traffic_total=traffic_total,
                traffic_remaining=traffic_remaining,
                traffic_used=traffic_used,
                traffic_up=client.up,
                traffic_down=client.down,
                expiry_time=expiry_time,
            )
            logger.debug(f"Successfully retrieved client data for {user_id}: {client_data}.")
            return client_data
        except Exception as exception:
            logger.error(f"Error retrieving client data for {user_id}: {exception}")
            return None

    async def get_key(self, user_id: int) -> str:
        """
        Generates the VPN key for a user.

        Arguments:
            user_id (int): The user ID to fetch the key for.

        Returns:
            str: The generated VPN key.
        """
        async with self.session() as session:
            user: User = await User.get(session, user_id=user_id)
        key = f"{self.subscription}{user.vpn_id}"
        logger.debug(f"Fetched key for {user_id}: {key}.")
        return key

    async def create_client(
        self,
        user: User,
        devices: int,
        duration: int,
        enable: bool = True,
        flow: str = "xtls-rprx-vision",
        total_gb: int = 0,
        inbound_id: int = 7,  # TODO: Make a server config
    ) -> bool:
        logger.info(f"Creating new client {user.user_id} | {devices} devices {duration} days.")
        new_client = Client(
            email=str(user.user_id),
            enable=enable,
            id=user.vpn_id,
            expiry_time=self._days_to_timestamp(duration),
            flow=flow,
            limit_ip=devices,
            sub_id=user.vpn_id,
            total_gb=total_gb,
        )
        """
        Creates a new client.

        Arguments:
            user (User): The user to create a client for.
            devices (int): The number of devices the client can use.
            duration (int): The subscription duration in days.
            enable (bool): Whether the client is enabled.
            flow (str): The traffic flow protocol.
            total_gb (int): The total data quota in GB.
            inbound_id (int): The inbound ID for the server.

        Returns:
            bool: True if the client was created successfully, False otherwise.
        """
        try:
            await self.api.client.add(inbound_id, [new_client])
            logger.info(f"Successfully created client for {user.user_id}.")
            return True
        except Exception as exception:
            logger.error(f"Error creating client for {user.user_id}: {exception}")
            return False

    async def update_client(
        self,
        user: User,
        devices: int,
        duration: int,
        replace_devices: bool = False,
        replace_duration: bool = False,
        enable: bool = True,
        flow: str = "xtls-rprx-vision",
        total_gb: int = 0,
    ) -> bool:
        """
        Updates an existing client.

        Arguments:
            user (User): The user whose client is to be updated.
            devices (int): The number of devices the client can use.
            duration (int): The subscription duration in days.
            replace_devices (bool): Whether to replace the devices limit.
            replace_duration (bool): Whether to replace the expiration date.
            enable (bool): Whether the client is enabled.
            flow (str): The traffic flow protocol.
            total_gb (int): The total data quota in GB.

        Returns:
            bool: True if the client was updated successfully, False otherwise.
        """
        logger.info(f"Updating client {user.user_id} | {devices} devices {duration} days.")

        try:
            client: Client = await self.api.client.get_by_email(str(user.user_id))

            if client is None:
                logger.debug(f"Client {user.user_id} not found for update.")
                return False

            if not replace_devices:
                current_device_limit = await self.get_limit_ip(client)
                devices = current_device_limit + devices

            current_time = self._current_timestamp()

            if not replace_duration:
                expiry_time_to_use = max(client.expiry_time, current_time)
            else:
                expiry_time_to_use = current_time

            expiry_time = self._add_days_to_timestamp(expiry_time_to_use, duration)

            client.enable = enable
            client.id = user.vpn_id
            client.expiry_time = expiry_time
            client.flow = flow
            client.limit_ip = devices
            client.sub_id = user.vpn_id
            client.total_gb = total_gb

            await self.api.client.update(client.id, client)
            logger.info(f"Client {user.user_id} updated successfully.")
            return True
        except Exception as exception:
            logger.error(f"Error updating client {user.user_id}: {exception}")
            return False

    async def create_subscription(self, user_id: int, devices: int, duration: int) -> bool:
        """
        Creates a new subscription for the user.

        Arguments:
            user_id (int): The user ID to create a subscription for.
            devices (int): The number of devices the user can use.
            duration (int): The subscription duration in days.

        Returns:
            bool: True if the subscription was created, False otherwise.
        """
        async with self.session() as session:
            user: User = await User.get(session, user_id=user_id)

        if not await self.is_client_exists(user.user_id):
            return await self.create_client(user, devices, duration)

        return await self.update_client(
            user,
            devices,
            duration,
            replace_devices=True,
            replace_duration=True,
        )

    async def extend_subscription(self, user_id: int, devices: int, duration: int) -> bool:
        """
        Extends the subscription for an existing user.

        Arguments:
            user_id (int): The user ID to extend the subscription for.
            devices (int): The number of devices the user can use.
            duration (int): The subscription extension duration in days.

        Returns:
            bool: True if the subscription was extended, False otherwise.
        """
        async with self.session() as session:
            user: User = await User.get(session, user_id=user_id)
        return await self.update_client(user, devices, duration, replace_devices=True)

    async def activate_promocode(self, user_id: int, promocode: Promocode) -> bool:
        """
        Activates a promocode for a user.

        Arguments:
            user_id (int): The user ID to activate the promocode for.
            promocode (Promocode): The promocode to activate.

        Returns:
            bool: True if the promocode was activated, False otherwise.
        """
        if not await self.promocode_service.activate_promocode(promocode.code, user_id):
            logger.debug(f"Failed to activate promocode {promocode.code} for user {user_id}.")
            return False

        async with self.session() as session:
            user: User = await User.get(session, user_id=user_id)

        if await self.is_client_exists(user_id):
            success = await self.update_client(user, devices=0, duration=promocode.duration)
            if success:
                logger.info(
                    f"Updated existing client for user {user_id} with promocode {promocode.code}."
                )
                return True
        else:
            success = await self.create_client(user, devices=1, duration=promocode.duration)
            if success:
                logger.info(
                    f"Created new client for user {user_id} with promocode {promocode.code}."
                )
                return True

        await self.promocode_service.deactivate_promocode(promocode.code)
        logger.warning(
            f"Promocode {promocode.code} deactivated due to client update/creation failure."
        )
        return False

    def _gb_to_bytes(self, traffic_gb: int) -> int:
        """
        Converts GB to bytes.

        Arguments:
            traffic_gb (int): The amount of traffic in GB.

        Returns:
            int: The equivalent amount of bytes.
        """
        bytes_in_gb = 1024**3
        return int(traffic_gb * bytes_in_gb)

    def _current_timestamp(self) -> int:
        """
        Returns the current timestamp in milliseconds.

        Returns:
            int: The current timestamp in milliseconds.
        """
        return int(datetime.now(timezone.utc).timestamp() * 1000)

    def _add_days_to_timestamp(self, timestamp: int, days: int) -> int:
        """
        Adds a specified number of days to a given timestamp.

        Arguments:
            timestamp (int): The original timestamp.
            days (int): The number of days to add.

        Returns:
            int: The updated timestamp.
        """
        current_datetime = datetime.fromtimestamp(timestamp / 1000, tz=timezone.utc)
        new_datetime = current_datetime + timedelta(days=days)
        return int(new_datetime.timestamp() * 1000)

    def _days_to_timestamp(self, days: int) -> int:
        """
        Converts a number of days to a timestamp.

        Arguments:
            days (int): The number of days to convert.

        Returns:
            int: The corresponding timestamp.
        """
        current_time = self._current_timestamp()
        return self._add_days_to_timestamp(current_time, days)
