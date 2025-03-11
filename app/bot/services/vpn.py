from __future__ import annotations

from typing import TYPE_CHECKING

from app.bot.utils.network import extract_base_url
from app.config import Config

if TYPE_CHECKING:
    from .server_pool import ServerPoolService

import logging

from py3xui import Client, Inbound
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ClientData
from app.bot.utils.time import (
    add_days_to_timestamp,
    days_to_timestamp,
    get_current_timestamp,
)
from app.db.models import Promocode, User, Referral

logger = logging.getLogger(__name__)


class VPNService:
    def __init__(
        self,
        config: Config,
        session: async_sessionmaker,
        server_pool_service: ServerPoolService,
    ) -> None:
        self.config = config
        self.session = session
        self.server_pool_service = server_pool_service
        logger.info("VPN Service initialized.")

    async def is_client_exists(self, user: User) -> Client | None:
        connection = await self.server_pool_service.get_connection(user)

        if not connection:
            return None

        client = await connection.api.client.get_by_email(str(user.tg_id))

        if client:
            logger.debug(f"Client {user.tg_id} exists on server {connection.server.name}.")
        else:
            logger.critical(f"Client {user.tg_id} not found on server {connection.server.name}.")

        return client

    async def get_limit_ip(self, user: User, client: Client) -> int | None:
        connection = await self.server_pool_service.get_connection(user)

        if not connection:
            return None

        try:
            inbounds: list[Inbound] = await connection.api.inbound.get_list()
        except Exception as exception:
            logger.error(f"Failed to fetch inbounds: {exception}")
            return None

        for inbound in inbounds:
            for inbound_client in inbound.settings.clients:
                if inbound_client.email == client.email:
                    logger.debug(f"Client {client.email} limit ip: {inbound_client.limit_ip}")
                    return inbound_client.limit_ip

        logger.critical(f"Client {client.email} not found in inbounds.")
        return None

    async def get_client_data(self, user: User) -> ClientData | None:
        logger.debug(f"Starting to retrieve client data for {user.tg_id}.")

        connection = await self.server_pool_service.get_connection(user)

        if not connection:
            return None

        try:
            client = await connection.api.client.get_by_email(str(user.tg_id))

            if not client:
                logger.critical(
                    f"Client {user.tg_id} not found on server {connection.server.name}."
                )
                return None

            limit_ip = await self.get_limit_ip(user=user, client=client)
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
            logger.debug(f"Successfully retrieved client data for {user.tg_id}: {client_data}.")
            return client_data
        except Exception as exception:
            logger.error(f"Error retrieving client data for {user.tg_id}: {exception}")
            return None

    async def get_key(self, user: User) -> str | None:
        async with self.session() as session:
            user = await User.get(session=session, tg_id=user.tg_id)

        if not user.server_id:
            logger.debug(f"Server ID for user {user.tg_id} not found.")
            return None

        subscription = extract_base_url(
            url=user.server.host,
            port=self.config.xui.SUBSCRIPTION_PORT,
            path=self.config.xui.SUBSCRIPTION_PATH,
        )
        key = f"{subscription}{user.vpn_id}"
        logger.debug(f"Fetched key for {user.tg_id}: {key}.")
        return key

    async def create_client(
        self,
        user: User,
        devices: int,
        duration: int,
        enable: bool = True,
        flow: str = "xtls-rprx-vision",
        total_gb: int = 0,
        inbound_id: int = 1,
    ) -> bool:
        logger.info(f"Creating new client {user.tg_id} | {devices} devices {duration} days.")

        await self.server_pool_service.assign_server_to_user(user)
        connection = await self.server_pool_service.get_connection(user)

        if not connection:
            return False

        new_client = Client(
            email=str(user.tg_id),
            enable=enable,
            id=user.vpn_id,
            expiry_time=days_to_timestamp(duration),
            flow=flow,
            limit_ip=devices,
            sub_id=user.vpn_id,
            total_gb=total_gb,
        )
        inbound_id = await self.server_pool_service.get_inbound_id(connection.api)

        try:
            await connection.api.client.add(inbound_id=inbound_id, clients=[new_client])
            logger.info(f"Successfully created client for {user.tg_id}")
            return True
        except Exception as exception:
            logger.error(f"Error creating client for {user.tg_id}: {exception}")
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
        logger.info(f"Updating client {user.tg_id} | {devices} devices {duration} days.")
        connection = await self.server_pool_service.get_connection(user)

        if not connection:
            return False

        try:
            client = await connection.api.client.get_by_email(str(user.tg_id))

            if client is None:
                logger.critical(f"Client {user.tg_id} not found for update.")
                return False

            if not replace_devices:
                current_device_limit = await self.get_limit_ip(user=user, client=client)
                devices = current_device_limit + devices

            current_time = get_current_timestamp()

            if not replace_duration:
                expiry_time_to_use = max(client.expiry_time, current_time)
            else:
                expiry_time_to_use = current_time

            expiry_time = add_days_to_timestamp(timestamp=expiry_time_to_use, days=duration)

            client.enable = enable
            client.id = user.vpn_id
            client.expiry_time = expiry_time
            client.flow = flow
            client.limit_ip = devices
            client.sub_id = user.vpn_id
            client.total_gb = total_gb

            await connection.api.client.update(client_uuid=client.id, client=client)
            logger.info(f"Client {user.tg_id} updated successfully.")
            return True
        except Exception as exception:
            logger.error(f"Error updating client {user.tg_id}: {exception}")
            return False

    async def create_subscription(self, user: User, devices: int, duration: int) -> bool:
        if not await self.is_client_exists(user):
            return await self.create_client(user=user, devices=devices, duration=duration)
        return False

    async def extend_subscription(self, user: User, devices: int, duration: int) -> bool:
        return await self.update_client(
            user=user,
            devices=devices,
            duration=duration,
            replace_devices=True,
        )

    async def change_subscription(self, user: User, devices: int, duration: int) -> bool:
        if await self.is_client_exists(user):
            return await self.update_client(
                user,
                devices,
                duration,
                replace_devices=True,
                replace_duration=True,
            )
        return False

    async def process_bonus_days(self, user: User, duration: int) -> bool:
        """
        Ensures that user will receive its bonus days both if it already has subscription, or not.

        Args:
            user (User): User object.
            duration (int): Duration of bonus days in days.

        Returns:
            bool: True, when bonus days have been successfully given, else False.
        """
        if await self.is_client_exists(user):
            updated = await self.update_client(user=user, devices=0, duration=duration)
            if updated:
                logger.info(f"Updated client {user.tg_id} with additional {duration} days(-s).")
                return True
        else:
            created = await self.create_client(user=user, devices=1, duration=duration)
            if created:
                logger.info(f"Created client {user.tg_id} with additional {duration} days(-s)")
                return True

        return False

    async def activate_promocode(self, user: User, promocode: Promocode) -> bool:
        # todo: consider moving to some 'promocode module services' with usage of vpn-service methods.

        async with self.session() as session:
            activated = await Promocode.set_activated(
                session=session,
                code=promocode.code,
                user_id=user.tg_id,
            )

        if not activated:
            logger.critical(f"Failed to activate promocode {promocode.code} for user {user.tg_id}.")
            return False

        logger.info(f"Begun applying promocode ({promocode.code}) to a client {user.tg_id}.")
        success = await self.process_bonus_days(user, duration=promocode.duration)

        if success:
            return True

        async with self.session() as session:
            await Promocode.set_deactivated(session=session, code=promocode.code)

        logger.warning(f"Promocode {promocode.code} not activated due to failure.")
        return False

    async def reward_referral(self, referred_tg_id: int) -> bool:
        """
        Rewards both user who invited (referrer) and who has been invited (referred).
        And calls database method to log this action.

        Args:
            referred_tg_id (int): Unique Telegram ID of referred user.

        Returns:
            bool: True, when the reward has been successfully given AT LEAST to a referred user, else False.
        """

        # todo: consider moving to some 'referral module services' with usage of vpn-service methods.

        async with self.session() as session:
            referral = await Referral.get_referral_with_users(session=session, referred_tg_id=referred_tg_id)

            if not referral:
                logger.warning(f"Referral not found for user {referred_tg_id}.")
                return False

            rewarded = await referral.set_rewarded(session=session, referral=referral)
            if not rewarded:
                logger.warning(f"Referral reward already given for {referred_tg_id}.")
                return False

            logger.info(f"Applying reward to referred user {referral.referred_tg_id}. Referral ID: {referral.id}")
            referred_success = await self.process_bonus_days(referral.referred,
                                                             duration=self.config.shop.REFERRAL_PERIOD)

            logger.info(f"Applying reward to referrer user {referral.referrer_tg_id}. Referral ID: {referral.id}")
            referrer_success = await self.process_bonus_days(referral.referrer,
                                                             duration=self.config.shop.REFERRAL_PERIOD)

        if referred_success and referrer_success:
            return True

        async with self.session() as session_local:
            await Referral.rollback_rewarded(
                session=session_local,
                referral=referral,
                rollback_referrer=not referrer_success,
                rollback_referred=not referred_success,
            )

        if not referrer_success and not referred_success:
            return False
        elif not referrer_success:
            logger.critical(
                f"Failed to reward referrer, but rewarded referred client. Referral ID: {referral.id}.")
            return True  # continue with no error, as referred user (who started rewards assigning) received its reward.

    async def gift_trial(self, user: User) -> bool:
        """
        Rewards both user who invited (referrer) and who has been invited (referred).

        Args:
            user (User): User object.

        Returns:
            bool: True, when the reward has been successfully given, else False.
        """

        # todo: consider moving to some 'referral module services' with usage of vpn-service methods.

        if not self.config.shop.TRIAL_ENABLED:
            logger.warning(f"Failed to activate trial for user {user.tg_id}. Trial period is disabled.")
            return False

        if user.is_trial_used is True:
            logger.info(f"User {user.tg_id} has already used Trial period before")
            return False

        async with self.session() as session:
            trial_used = await User.update_trial_status(session=session, tg_id=user.tg_id, used=True)

        if not trial_used:
            logger.critical(f"Failed to activate trial for user {user.tg_id}.")
            return False

        logger.info(f"Begun applying trial period for user {user.tg_id}.")
        trial_success = await self.process_bonus_days(user, duration=self.config.shop.TRIAL_PERIOD)

        if trial_success:
            return True

        async with self.session() as session:
            await User.update_trial_status(session=session, tg_id=user.tg_id, used=False)

        logger.warning(f"Failed to apply trial period for user {user.tg_id} due to failure.")
        return False
