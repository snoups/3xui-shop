import logging
from dataclasses import dataclass
from logging.handlers import MemoryHandler
from pathlib import Path

from environs import Env
from marshmallow.validate import OneOf

from app.bot.utils.constants import (
    DB_FORMAT,
    LOG_GZ_ARCHIVE_FORMAT,
    LOG_ZIP_ARCHIVE_FORMAT,
    Currency,
)

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_DATA_DIR = BASE_DIR / "data"
DEFAULT_LOCALES_DIR = BASE_DIR / "locales"
DEFAULT_PLANS_DIR = DEFAULT_DATA_DIR / "plans.json"

DEFAULT_BOT_HOST = "0.0.0.0"
DEFAULT_BOT_PORT = 8080

DEFAULT_SHOP_EMAIL = "support@3xui-shop.com"
DEFAULT_SHOP_CURRENCY = Currency.RUB.code
DEFAULT_SHOP_TRIAL_ENABLED = True
DEFAULT_SHOP_TRIAL_PERIOD = 3
DEFAULT_SHOP_PAYMENT_STARS_ENABLED = True
DEFAULT_SHOP_PAYMENT_CRYPTOMUS_ENABLED = False
DEFAULT_SHOP_PAYMENT_YOOKASSA_ENABLED = False

DEFAULT_DB_NAME = "bot_database"

DEFAULT_REDIS_DB_NAME = "0"
DEFAULT_REDIS_HOST = "3xui-shop-redis"
DEFAULT_REDIS_PORT = 6379

DEFAULT_SUBSCRIPTION_PORT = 2096
DEFAULT_SUBSCRIPTION_PATH = "/user/"

DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DEFAULT_LOG_ARCHIVE_FORMAT = LOG_ZIP_ARCHIVE_FORMAT

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
memory_handler = MemoryHandler(capacity=100, flushLevel=logging.ERROR)
memory_handler.setFormatter(logging.Formatter(DEFAULT_LOG_FORMAT))
logger.addHandler(memory_handler)


@dataclass
class BotConfig:
    """
    Configuration for the Telegram bot.

    Attributes:
        TOKEN (str): API token for the Telegram bot.
        ADMINS (list[int]): List of admin IDs (user IDs) for admin tools.
        DEV_ID (int): Developer ID (user ID) for notifications.
        SUPPORT_ID (int): Support ID (user ID) for support.
        DOMAIN (str): Domain for the application.
        PORT (int): Port for the application.

    """

    TOKEN: str
    ADMINS: list[int]
    DEV_ID: int
    SUPPORT_ID: int
    DOMAIN: str
    PORT: int


@dataclass
class ShopConfig:
    """
    Configuration for the shop.

    Attributes:
        EMAIL (str): Email address for receipts.
        CURRENCY (str): Default currency for buttons.
        TRIAL_ENABLED (bool): Flag indicating if trial period is enabled.
        TRIAL_PERIOD (int): Trial period in days.
        PAYMENT_STARS_ENABLED (bool): Flag indicating if Stars payment method is enabled.
        PAYMENT_CRYPTOMUS_ENABLED (bool): Flag indicating if Cryptomus payment method is enabled.
        PAYMENT_YOOKASSA_ENABLED (bool): Flag indicating if Yookassa payment method is enabled.

    """

    EMAIL: str
    CURRENCY: str
    TRIAL_ENABLED: bool
    TRIAL_PERIOD: int
    PAYMENT_STARS_ENABLED: bool
    PAYMENT_CRYPTOMUS_ENABLED: bool
    PAYMENT_YOOKASSA_ENABLED: bool


@dataclass
class XUIConfig:
    """
    Configuration for XUI.

    Attributes:
        USERNAME (str): Username for XUI authentication.
        PASSWORD (str): Password for XUI authentication.
        TOKEN (str | None): API token for XUI (if provided).
        SUBSCRIPTION_PORT (int): Port number for subscription.
        SUBSCRIPTION_PATH (str): URL path for subscription.
    """

    USERNAME: str
    PASSWORD: str
    TOKEN: str | None
    SUBSCRIPTION_PORT: int
    SUBSCRIPTION_PATH: str


@dataclass
class YooKassaConfig:
    """
    Configuration for YooKassa.

    Attributes:
        TOKEN (str | None): API token for YooKassa.
        SHOP_ID (int | None): Shop ID for YooKassa.
    """

    TOKEN: str | None
    SHOP_ID: int | None


@dataclass  
class CryptomusConfig:
    """
    Configuration for Cryptomus.

    API_KEY: str
    MERCHANT_ID: str
    """

    API_KEY: str
    MERCHANT_ID: str



@dataclass
class DatabaseConfig:
    """
    Configuration for Database.

    Attributes:
        HOST (str | None): Host address of DataBase server.
        PORT (int | None): Port number for Database server.
        USERNAME (str | None): Username for Database authentication.
        PASSWORD (str | None): Password for Database authentication.
        NAME (str): Name of Database to connect to.
    """

    HOST: str | None
    PORT: int | None
    NAME: str
    USERNAME: str | None
    PASSWORD: str | None

    def url(self, driver: str = "sqlite+aiosqlite") -> str:
        """
        Generates a database connection URL using the provided driver, username,
        password, host, port, and database name.

        Arguments:
            driver (str): Driver to use for the connection. Defaults to "sqlite+aiosqlite".

        Returns:
            str: Generated connection URL.
        """
        if driver.startswith("sqlite"):
            return f"{driver}:////{DEFAULT_DATA_DIR}/{self.NAME}.{DB_FORMAT}"
        return f"{driver}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


@dataclass
class RedisConfig:
    """
    Configuration for Redis.

    Attributes:
        HOST (str): Host address of Redis server.
        PORT (int): Port number for Redis server.
        DB_NAME (str): Name of Redis database.
        USERNAME (str | None): Username for Redis authentication.
        PASSWORD (str | None): Password for Redis authentication.
    """

    HOST: str
    PORT: int
    DB_NAME: str
    USERNAME: str | None
    PASSWORD: str | None

    def url(self) -> str:
        if self.USERNAME and self.PASSWORD:
            return f"redis://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB_NAME}"
        return f"redis://{self.HOST}:{self.PORT}/{self.DB_NAME}"


@dataclass
class LoggingConfig:
    """
    Configuration for logging.

    Attributes:
        LEVEL (str): Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        FORMAT (str): Format string for log messages.
        ARCHIVE_FORMAT (str): Archive format for log archiving (either "zip" or "gz").
    """

    LEVEL: str
    FORMAT: str
    ARCHIVE_FORMAT: str


@dataclass
class Config:
    """
    Main configuration class for the application.

    Contains all configurations related to the Bot, Shop, XUI,
    YooKassa, Database, Redis and Logging.

    Attributes:
        bot (BotConfig): Bot configuration.
        shop (ShopConfig): Shop configuration.
        xui (XUIConfig): XUI configuration.
        yookassa (YooKassaConfig): YooKassa configuration.
        database (DatabaseConfig): Database configuration.
        redis (RedisConfig): Redis configuration.
        logging (LoggingConfig): Logging configuration.
    """

    bot: BotConfig
    shop: ShopConfig
    xui: XUIConfig
    yookassa: YooKassaConfig
    cryptomus: CryptomusConfig
    database: DatabaseConfig
    redis: RedisConfig
    logging: LoggingConfig


def load_config() -> Config:
    """
    Load configuration from environment variables using `environs`.

    This function reads the environment variables and returns a fully populated
    `Config` object containing Bot, Shop, XUI, YooKassa, Database, Redis and Logging configurations.

    Returns:
        Config: A fully populated configuration object for the application.
    """
    env = Env()
    env.read_env()

    bot_admins = env.list("BOT_ADMINS", subcast=int, default=[], required=False)
    if not bot_admins:
        logger.warning("BOT_ADMINS list is empty.")

    xui_token = env.str("XUI_TOKEN", default=None)
    if not xui_token:
        logger.warning("XUI_TOKEN is not set.")

    payment_stars_enabled = env.bool(
        "SHOP_PAYMENT_STARS_ENABLED",
        default=DEFAULT_SHOP_PAYMENT_STARS_ENABLED,
    )

    payment_yookassa_enabled = env.bool(
        "SHOP_PAYMENT_YOOKASSA_ENABLED",
        default=DEFAULT_SHOP_PAYMENT_YOOKASSA_ENABLED,
    )
    if payment_yookassa_enabled:
        yookassa_token = env.str("YOOKASSA_TOKEN", default=None)
        if not yookassa_token:
            logger.error("YOOKASSA_TOKEN is not set. Payment YooKassa is disabled.")
            payment_yookassa_enabled = False

    payment_cryptomus_enabled = env.bool(
        "SHOP_PAYMENT_CRYPTOMUS_ENABLED",
        default=DEFAULT_SHOP_PAYMENT_CRYPTOMUS_ENABLED,
    )
    if payment_cryptomus_enabled:
        cryptomus_api_key = env.str("CRYPTOMUS_API_KEY", default=None)
        cryptomus_merchant_id = env.str("CRYPTOMUS_MERCHANT_ID", default=None)
        if not cryptomus_api_key or not cryptomus_merchant_id:
            logger.error("CRYPTOMUS_API_KEY or CRYPTOMUS_MERCHANT_ID is not set. Payment Cryptomus is disabled.")
            payment_cryptomus_enabled = False

    if not payment_yookassa_enabled and not payment_cryptomus_enabled and not payment_stars_enabled:
        logger.warning("No payment methods are enabled. Enabling Stars payment method.")
        payment_stars_enabled = True

    return Config(
        bot=BotConfig(
            TOKEN=env.str("BOT_TOKEN"),
            ADMINS=bot_admins,
            DEV_ID=env.int("BOT_DEV_ID"),
            SUPPORT_ID=env.int("BOT_SUPPORT_ID"),
            DOMAIN=f"https://{env.str('BOT_DOMAIN')}/",
            PORT=env.int("BOT_PORT", default=DEFAULT_BOT_PORT),
        ),
        shop=ShopConfig(
            EMAIL=env.str("SHOP_EMAIL", default=DEFAULT_SHOP_EMAIL),
            CURRENCY=env.str(
                "SHOP_CURRENCY",
                default=DEFAULT_SHOP_CURRENCY,
                validate=OneOf(
                    [currency.code for currency in Currency]
                    + [currency.code.lower() for currency in Currency],
                    error="SHOP_CURRENCY must be one of: {choices}",
                ),
            ).upper(),
            TRIAL_ENABLED=env.bool("SHOP_TRIAL_ENABLED", default=DEFAULT_SHOP_TRIAL_ENABLED),
            TRIAL_PERIOD=env.int("SHOP_TRIAL_PERIOD", default=DEFAULT_SHOP_TRIAL_PERIOD),
            PAYMENT_STARS_ENABLED=payment_stars_enabled,
            PAYMENT_CRYPTOMUS_ENABLED=payment_cryptomus_enabled,
            PAYMENT_YOOKASSA_ENABLED=payment_yookassa_enabled,
        ),
        xui=XUIConfig(
            USERNAME=env.str("XUI_USERNAME"),
            PASSWORD=env.str("XUI_PASSWORD"),
            TOKEN=xui_token,
            SUBSCRIPTION_PORT=env.int("XUI_SUBSCRIPTION_PORT", default=DEFAULT_SUBSCRIPTION_PORT),
            SUBSCRIPTION_PATH=env.str(
                "XUI_SUBSCRIPTION_PATH",
                default=DEFAULT_SUBSCRIPTION_PATH,
            ),
        ),
        yookassa=YooKassaConfig(
            TOKEN=env.str("YOOKASSA_TOKEN", default=None),
            SHOP_ID=env.int("YOOKASSA_SHOP_ID", default=None),
        ),
        cryptomus=CryptomusConfig(
            API_KEY=env.str("CRYPTOMUS_API_KEY", default=None),
            MERCHANT_ID=env.str("CRYPTOMUS_MERCHANT_ID", default=None),
        ),
        database=DatabaseConfig(
            HOST=env.str("DB_HOST", default=None),
            PORT=env.int("DB_PORT", default=None),
            USERNAME=env.str("DB_USERNAME", default=None),
            PASSWORD=env.str("DB_PASSWORD", default=None),
            NAME=env.str("DB_NAME", default=DEFAULT_DB_NAME),
        ),
        redis=RedisConfig(
            HOST=env.str("REDIS_HOST", default=DEFAULT_REDIS_HOST),
            PORT=env.int("REDIS_PORT", default=DEFAULT_REDIS_PORT),
            DB_NAME=env.str("REDIS_DB_NAME", default=DEFAULT_REDIS_DB_NAME),
            USERNAME=env.str("REDIS_USERNAME", default=None),
            PASSWORD=env.str("REDIS_PASSWORD", default=None),
        ),
        logging=LoggingConfig(
            LEVEL=env.str("LOG_LEVEL", default=DEFAULT_LOG_LEVEL),
            FORMAT=env.str("LOG_FORMAT", default=DEFAULT_LOG_FORMAT),
            ARCHIVE_FORMAT=env.str(
                "LOG_ARCHIVE_FORMAT",
                default=DEFAULT_LOG_ARCHIVE_FORMAT,
                validate=OneOf(
                    [LOG_ZIP_ARCHIVE_FORMAT, LOG_GZ_ARCHIVE_FORMAT],
                    error="LOG_ARCHIVE_FORMAT must be one of: {choices}",
                ),
            ),
        ),
    )
