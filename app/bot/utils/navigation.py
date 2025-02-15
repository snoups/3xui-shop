from enum import Enum


class NavMain(str, Enum):
    START = "start"
    MAIN_MENU = "main_menu"
    CLOSE_NOTIFICATION = "close_notification"
    REDIRECT_TO_DOWNLOAD = "redirect_to_download"


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
    CHANGE = "change"
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
    MAINTENANCE_MODE_ENABLE = "maintenance_mode_enable"
    MAINTENANCE_MODE_DISABLE = "maintenance_mode_disable"

    RESTART_BOT = "restart_bot"
