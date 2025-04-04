from aiogram import Bot
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n
from aiohttp.web import Application
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.bot.models import ServicesContainer
from app.config import Config

from ._gateway import PaymentGateway
from .cryptomus import Cryptomus
from .heleket import Heleket
from .telegram_stars import TelegramStars
from .yookassa import Yookassa
from .yoomoney import Yoomoney


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
        dependencies = [app, config, session, storage, bot, i18n, services]

        gateways = [
            (config.shop.PAYMENT_STARS_ENABLED, TelegramStars),
            (config.shop.PAYMENT_CRYPTOMUS_ENABLED, Cryptomus),
            (config.shop.PAYMENT_HELEKET_ENABLED, Heleket),
            (config.shop.PAYMENT_YOOKASSA_ENABLED, Yookassa),
            (config.shop.PAYMENT_YOOMONEY_ENABLED, Yoomoney),
        ]

        for enabled, gateway_cls in gateways:
            if enabled:
                self.register_gateway(gateway_cls(*dependencies))
