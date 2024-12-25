from enum import Enum

from aiogram.filters.callback_data import CallbackData


class Navigation(str, Enum):
    START = "start"
    MAIN_MENU = "main_menu"
    REFERRAL = "referral"
    PROMOCODE = "promocode"

    # region: Profile
    PROFILE = "profile"
    SHOW_KEY = "show_key"
    # endregion

    # region: Subscription
    ADMIN_TOOLS = "admin_tools"
    STATISTICS = "statistics"
    EDITOR_USERS = "editor_users"

    EDITOR_PROMOCODES = "editor_promocodes"
    CREATE_PROMOCODE = "create_promocode"
    DELETE_PROMOCODE = "delete_promocode"
    EDIT_PROMOCODE = "edit_promocode"

    SEND_NOTIFICATION = "send_notification"
    CREATE_BACKUP = "create_backup"
    RESTART_BOT = "restart_bot"
    # endregion

    # region: Subscription
    SUBSCRIPTION = "subscription"
    EXTEND = "extend"
    PROCESS = "process"
    DEVICES = "devices"
    DURATION = "duration"

    PAY = "pay"
    PAY_YOOKASSA = f"{PAY}_yookassa"
    PAY_TELEGRAM_STARS = f"{PAY}_telegram_stars"
    PAY_CRYPTOMUS = f"{PAY}_cryptomus"

    BACK_TO_DURATION = "back_to_duration"
    BACK_TO_PAYMENT = "back_to_payment"
    # endregion

    # region: Download
    DOWNLOAD = "download"
    PLATFORM = "platform"
    PLATFORM_IOS = f"{PLATFORM}_ios"
    PLATFORM_ANDROID = f"{PLATFORM}_android"
    PLATFORM_WINDOWS = f"{PLATFORM}_windows"
    # endregion

    # region: Support
    SUPPORT = "support"
    HOW_TO_CONNECT = "how_to_connect"
    VPN_NOT_WORKING = "vpn_not_working"
    # endregion


class SubscriptionCallback(CallbackData, prefix="subscription"):
    state: Navigation
    is_extend: bool = False
    user_id: int
    message_id: int = 0
    devices: int = 0
    duration: int = 0
    price: int = 0


class CreatePromocodeCallback(CallbackData, prefix="create_promocode"):
    state: Navigation
    duration: int = 0
