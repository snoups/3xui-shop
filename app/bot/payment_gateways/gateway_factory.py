from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiohttp.web import Application
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer
from app.config import Config

from ._gateway import PaymentGateway
from .telegram_stars import TelegramStars
from .yookassa import Yookassa
from .cryptomus import Cryptomus


class GatewayFactory:
    def __init__(self) -> None:
        self._gateways: dict[str, PaymentGateway] = {}

    def register_gateway(self, gateway: PaymentGateway) -> None:
        self._gateways[gateway.callback] = gateway

    def get_gateway(self, name: str) -> PaymentGateway:
        gateway = self._gateways.get(name)
        if not gateway:
            raise ValueError(f"Gateway {name} is not registered.")
        return gateway

    def get_gateways(self) -> list[PaymentGateway]:
        return list(self._gateways.values())

    def register_gateways(
        self,
        app: Application,
        config: Config,
        session: async_sessionmaker,
        storage: RedisStorage,
        bot: Bot,
        i18n: I18n,
        services: ServicesContainer,
    ) -> None:
        if config.shop.PAYMENT_STARS_ENABLED:
            self.register_gateway(
                TelegramStars(
                    config=config,
                    session=session,
                    bot=bot,
                    services=services,
                )
            )

        if config.shop.PAYMENT_YOOKASSA_ENABLED:
            self.register_gateway(
                Yookassa(
                    app=app,
                    config=config,
                    session=session,
                    storage=storage,
                    bot=bot,
                    i18n=i18n,
                    services=services,
                )
            )
        if config.shop.PAYMENT_CRYPTOMUS_ENABLED:
            self.register_gateway(
                Cryptomus(
                    app=app,
                    config=config,
                    session=session,
                    storage=storage,
                    bot=bot,
                    i18n=i18n,
                    services=services,
                )
            )
