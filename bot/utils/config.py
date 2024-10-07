import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

# Default values for logger configurations
DEFAULT_LOG_LEVEL = "DEBUG"
DEFAULT_LOG_FORMAT = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
DEFAULT_LOG_DIR = "logs"
DEFAULT_LOG_ARCHIVE_DIR = "logs/archive"

# Default values for localization configurations
DEFAULT_LOC_LANG = "EN"
DEFAULT_LOC_YAML_PATH = "bot/localization.yaml"

# Default value for database configurations
DEFAULT_DB_URL = "sqlite+aiosqlite:///./bot_database.db"


def get_env_var(name: str, required: bool = True) -> str | None:
    """
    Retrieves the value of an environment variable by its name.

    Args:
        name (str): The name of the environment variable to retrieve.
        required (bool): Whether the environment variable is required. Defaults to True.

    Returns:
        str | None: The value of the environment variable or None if not required and not set.

    Raises:
        ValueError: If the environment variable is required but not set or empty.
    """
    value = os.getenv(name)
    if required and not value:
        raise ValueError(f"Environment variable '{name}' is required but not set or empty.")
    return value


@dataclass(frozen=True)
class BotConfig:
    """
    Configuration for the Telegram bot.

    Attributes:
        token (str): The API token for the Telegram bot.
    """

    token: str

    @staticmethod
    def from_env() -> "BotConfig":
        """
        Creates an instance of BotConfig by reading environment variables.

        Returns:
            BotConfig: An instance of BotConfig with the token set.

        Raises:
            ValueError: If the BOT_TOKEN environment variable is not set.
        """
        token = get_env_var("BOT_TOKEN")
        return BotConfig(token=token)


@dataclass(frozen=True)
class XUIConfig:
    """
    Configuration for XUI.

    Attributes:
        host (str): The host URL for the XUI service.
        username (str): The username for XUI authentication.
        password (str): The password for XUI authentication.
        token (str | None): The API token for XUI. Defaults to an empty string if not provided.
    """

    host: str
    username: str
    password: str
    token: str | None

    @staticmethod
    def from_env() -> "XUIConfig":
        """
        Creates an instance of XUIConfig by reading environment variables.

        Returns:
            XUIConfig: An instance of XUIConfig with all attributes set.

        Raises:
            ValueError: If any of the required XUI environment variables are not set.
        """
        host = get_env_var("XUI_HOST")
        username = get_env_var("XUI_USERNAME")
        password = get_env_var("XUI_PASSWORD")
        token = get_env_var("XUI_TOKEN", required=False)
        return XUIConfig(host=host, username=username, password=password, token=token)


@dataclass(frozen=True)
class LogConfig:
    """
    Configuration for logging.

    Attributes:
        level (str): Logging level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL).
        format (str): Format string for log messages.
        dir (str): Directory where log files are stored.
        archive_dir (str): Directory where archived log files are stored.
    """

    level: str
    format: str
    dir: str
    archive_dir: str

    @staticmethod
    def from_env() -> "LogConfig":
        """
        Creates an instance of LogConfig by reading environment variables.

        Provides default values if certain environment variables are not set.

        Returns:
            LogConfig: An instance of LogConfig with all attributes set.
        """
        level = get_env_var("LOG_LEVEL", required=False) or DEFAULT_LOG_LEVEL
        log_format = get_env_var("LOG_FORMAT", required=False) or DEFAULT_LOG_FORMAT
        log_dir = get_env_var("LOG_DIR", required=False) or DEFAULT_LOG_DIR
        archive_dir = get_env_var("LOG_ARCHIVE_DIR", required=False) or DEFAULT_LOG_ARCHIVE_DIR
        return LogConfig(level=level, format=log_format, dir=log_dir, archive_dir=archive_dir)


@dataclass(frozen=True)
class LocConfig:
    """
    Configuration for localization.

    Attributes:
        default_lang (str): The default language code (e.g., "EN", "RU").
        yaml_path (str): The path to the localization YAML file.
    """

    default_lang: str
    yaml_path: str

    @staticmethod
    def from_env() -> "LocConfig":
        """
        Creates an instance of LocConfig by reading environment variables.

        Provides default values if certain environment variables are not set.

        Returns:
            LocConfig: An instance of LocConfig with all attributes set.
        """
        default_lang = get_env_var("LOC_DEFAULT_LANG", required=False) or DEFAULT_LOC_LANG
        yaml_path = get_env_var("LOC_YAML_PATH", required=False) or DEFAULT_LOC_YAML_PATH
        return LocConfig(default_lang=default_lang, yaml_path=yaml_path)


@dataclass(frozen=True)
class DBConfig:
    """
    Configuration for the database.

    Attributes:
        url (str): Database connection string.
    """

    url: str

    @staticmethod
    def from_env() -> "DBConfig":
        """
        Creates an instance of DBConfig by reading environment variables.

        Returns:
            DBConfig: An instance of DBConfig with the database URL set.
        """
        db_url = get_env_var("DB_URL", required=False) or DEFAULT_DB_URL
        return DBConfig(url=db_url)


@dataclass(frozen=True)
class Config:
    """
    Main configuration for the application.

    Attributes:
        bot (BotConfig): Configuration settings for the Telegram bot.
        xui (XUIConfig): Configuration settings for XUI.
        log (LogConfig): Configuration settings for logging.
        loc (LocConfig): Configuration settings for localization.
        db (DBConfig): Configuration settings for the database.
    """

    bot: BotConfig
    xui: XUIConfig
    log: LogConfig
    loc: LocConfig
    db: DBConfig

    @staticmethod
    def load() -> "Config":
        """
        Load all configuration settings.

        Returns:
            Config: Config object containing bot, xui, log, localization, and database configurations.
        """
        return Config(
            bot=BotConfig.from_env(),
            xui=XUIConfig.from_env(),
            log=LogConfig.from_env(),
            loc=LocConfig.from_env(),
            db=DBConfig.from_env(),
        )


config: Config = Config.load()
