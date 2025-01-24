from enum import Enum

from aiogram.filters.callback_data import CallbackData


class NavMain(str, Enum):
    START = "start"
    MAIN_MENU = "main_menu"
    CLOSE_NOTIFICATION = "close_notification"


class NavProfile(str, Enum):
    MAIN = "profile"
    SHOW_KEY = "show_key"


class NavReferral(str, Enum):
    MAIN = "referral"


class NavSupport(str, Enum):
    MAIN = "support"
    HOW_TO_CONNECT = "how_to_connect"
    VPN_NOT_WORKING = "vpn_not_working"


class NavDownload(str, Enum):
    MAIN = "download"
    PLATFORM = "platform"
    PLATFORM_IOS = f"{PLATFORM}_ios"
    PLATFORM_ANDROID = f"{PLATFORM}_android"
    PLATFORM_WINDOWS = f"{PLATFORM}_windows"


class NavSubscription(str, Enum):
    MAIN = "subscription"
    EXTEND = "extend"
    PROCESS = "process"
    DEVICES = "devices"
    DURATION = "duration"
    PROMOCODE = "promocode"

    PAY = "pay"
    PAY_YOOKASSA = f"{PAY}_yookassa"
    PAY_TELEGRAM_STARS = f"{PAY}_telegram_stars"
    PAY_CRYPTOMUS = f"{PAY}_cryptomus"

    BACK_TO_DURATION = "back_to_duration"
    BACK_TO_PAYMENT = "back_to_payment"


class NavAdminTools(str, Enum):
    MAIN = "admin_tools"
    TEST = "test"
    SERVER_MANAGEMENT = "server_management"
    SHOW_SERVER = "show_server"
    PING_SERVER = "ping_server"
    ADD_SERVER = "add_server"
    ADD_SERVER_BACK = "add_server_back"
    СONFIRM_ADD_SERVER = "сonfirm_add_server"
    DELETE_SERVER = "delete_server"
    EDIT_SERVER = "edit_server"

    STATISTICS = "statistics"
    USER_EDITOR = "user_editor"

    PROMOCODE_EDITOR = "promocode_editor"
    CREATE_PROMOCODE = "create_promocode"
    DELETE_PROMOCODE = "delete_promocode"
    EDIT_PROMOCODE = "edit_promocode"

    SEND_NOTIFICATION = "send_notification"
    CREATE_BACKUP = "create_backup"

    MAINTENANCE_MODE = "maintenance_mode"
    MAINTENANCE_ON = "maintenance_on"
    MAINTENANCE_OFF = "maintenance_off"

    RESTART_BOT = "restart_bot"


class SubscriptionData(CallbackData, prefix="subscription"):
    state: NavSubscription
    is_extend: bool = False
    user_id: int = 0
    message_id: int = 0
    devices: int = 0
    duration: int = 0
    price: int = 0


class TransactionStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


V2RAYTUN_IOS_LINK = "https://apps.apple.com/ru/app/v2raytun/id6476628951"
V2RAYTUN_ANDROID_LINK = "https://play.google.com/store/apps/details?id=com.v2raytun.android"
HIDDIFY_WINDOWS_LINK = (
    "https://github.com/hiddify/hiddify-next/releases/download/"
    "v2.0.5/Hiddify-Windows-Setup-x64.exe"
)

MAIN_MESSAGE_ID_KEY = "main_message_id"
PREVIOUS_CALLBACK_KEY = "previous_callback"
