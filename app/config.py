from dataclasses import dataclass
from pathlib import Path

from environs import Env

BASE_DIR = Path(__file__).resolve().parent

# Default values for database
DEFAULT_DB_NAME = "bot_database"


@dataclass
class BotConfig:
    """
    Configuration for the Telegram bot.

    Attributes:
        TOKEN (str): The API token for the Telegram bot.
        DEV_ID (int): TODO

    """

    TOKEN: str
    DEV_ID: int


@dataclass
class DatabaseConfig:
    """
    TODO

    Attributes:
        USERNAME (str): TODO
        PASSWORD (str): TODO
        NAME (str): TODO
        HOST (str): TODO
        PORT (int): TODO
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
class Config:
    """
    TODO

    Attributes:
        bot (BotConfig): TODO
        database (DatabaseConfig): TODO
    """

    bot: BotConfig
    database: DatabaseConfig


def load_config() -> Config:
    """
    TODO

    Returns:
        TODO
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
    )
