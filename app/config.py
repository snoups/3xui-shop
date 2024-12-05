from dataclasses import dataclass
from pathlib import Path

from environs import Env
from marshmallow.validate import OneOf

BASE_DIR = Path(__file__).resolve().parent

# Default values for database
DEFAULT_DB_NAME = "bot_database"

# Default values for logging configurations
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DEFAULT_LOG_DIR = "./logs"
DEFAULT_LOG_ARCHIVE_FORMAT = "zip"


@dataclass
class BotConfig:
    """
    Configuration for the Telegram bot.

    Attributes:
        TOKEN (str): The API token for the Telegram bot.
        DEV_ID (int): Developer ID (user_id) for notifications.
    """

    TOKEN: str
    DEV_ID: int


@dataclass
class DatabaseConfig:  # TODO: Add support for different drivers
    """
    Configuration for the database.

    Attributes:
        USERNAME (str): Username for database authentication.
        PASSWORD (str): Password for database authentication.
        NAME (str): Name of the database to connect to.
        HOST (str): Host address of the database server.
        PORT (int): Port number for the database server.
    """

    USERNAME: str
    PASSWORD: str
    NAME: str
    HOST: str
    PORT: int

    def url(self, driver: str = "sqlite+aiosqlite") -> str:
        """
        Generates a database connection URL using the provided driver,
        username, password, host, port, and database.

        Args:
            driver (str): The driver to use for the connection. Defaults to "sqlite+aiosqlite".
        Returns:
            The generated connection URL.
        """
        if driver.startswith("sqlite"):
            return f"{driver}:///./{self.NAME}.db"
        return f"{driver}://{self.USERNAME}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.NAME}"


@dataclass
class LoggingConfig:
    """
    Configuration for logging.

    Attributes:
        LEVEL (str): Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        FORMAT (str): Format string for log messages.
        DIR (str): Directory where log files are stored.
        ARCHIVE_FORMAT (str): Archive format for log archiving.
    """

    LEVEL: str
    FORMAT: str
    DIR: str
    ARCHIVE_FORMAT: str


@dataclass
class Config:
    """
    Main configuration class.

    Attributes:
        bot (BotConfig): Bot configuration.
        database (DatabaseConfig): Database configuration.
        logging (LoggingConfig): Logging configuration.
    """

    bot: BotConfig
    database: DatabaseConfig
    logging: LoggingConfig


def load_config() -> Config:
    """
    Load configuration from environment variables.

    Returns:
        Config: The application configuration.
    """
    env = Env()
    env.read_env()

    return Config(
        bot=BotConfig(
            TOKEN=env.str("BOT_TOKEN"),
            DEV_ID=env.int("BOT_DEV_ID"),
        ),
        database=DatabaseConfig(
            HOST=env.str("DB_HOST", ""),
            PORT=env.int("DB_PORT", 0),
            USERNAME=env.str("DB_USERNAME", ""),
            PASSWORD=env.str("DB_PASSWORD", ""),
            NAME=env.str("DB_NAME", "bot_database"),
        ),
        logging=LoggingConfig(
            LEVEL=env.str("LOG_LEVEL", DEFAULT_LOG_LEVEL),
            FORMAT=env.str("LOG_FORMAT", DEFAULT_LOG_FORMAT),
            DIR=env.str("LOG_DIR", DEFAULT_LOG_DIR),
            ARCHIVE_FORMAT=env.str(
                "LOG_ARCHIVE_FORMAT",
                DEFAULT_LOG_ARCHIVE_FORMAT,
                validate=OneOf(["zip", "gz"], error="LOG_ARCHIVE_FORMAT must be one of: {choices}"),
            ),
        ),
    )
