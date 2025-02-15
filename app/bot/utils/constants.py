V2RAYTUN_IOS_LINK = "https://apps.apple.com/ru/app/v2raytun/id6476628951"
V2RAYTUN_ANDROID_LINK = "https://play.google.com/store/apps/details?id=com.v2raytun.android"
HIDDIFY_WINDOWS_LINK = (
    "https://github.com/hiddify/hiddify-next/releases/download/"
    "v2.0.5/Hiddify-Windows-Setup-x64.exe"
)

MAIN_MESSAGE_ID_KEY = "main_message_id"
PREVIOUS_CALLBACK_KEY = "previous_callback"

INPUT_PROMOCODE_KEY = "input_promocode"

SERVER_NAME_KEY = "server_name"
SERVER_HOST_KEY = "server_host"
SERVER_SUBSCRIPTION_KEY = "server_subscription"
SERVER_MAX_CLIENTS_KEY = "server_max_clients"

# Webhook paths
TELEGRAM_WEBHOOK = "/webhook"  # Webhook path for Telegram bot updates
YOOKASSA_WEBHOOK = "/yookassa"  # Webhook path for receiving Yookassa payment notifications
CONNECTION_WEBHOOK = "/connection"  # Webhook path for receiving connection requests

# Notification tags
BOT_STARTED_TAG = "#BotStarted"
BOT_STOPPED_TAG = "#BotStopped"
BACKUP_CREATED_TAG = "#BackupCreated"

# I18n settings
DEFAULT_LANGUAGE = "en"
I18N_DOMAIN = "bot"

UNLIMITED = "∞"
DB_FORMAT = "sqlite3"
LOG_ZIP_ARCHIVE_FORMAT = "zip"
LOG_GZ_ARCHIVE_FORMAT = "gz"

MESSAGE_EFFECT_IDS = {
    "🔥": "5104841245755180586",
    "👍": "5107584321108051014",
    "👎": "5104858069142078462",
    "❤️": "5044134455711629726",
    "🎉": "5046509860389126442",
    "💩": "5046589136895476101",
}

from enum import Enum


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELED = "canceled"
    REFUNDED = "refunded"


class Currency(Enum):
    RUB = "RUB"
    USD = "USD"
    XTR = "XTR"


class CurrencySymbol(Enum):
    RUB = "₽"
    USD = "$"
    XTR = "★"
