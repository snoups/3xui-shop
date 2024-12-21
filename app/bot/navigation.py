from enum import Enum

from aiogram.filters.callback_data import CallbackData


class NavigationAction(str, Enum):
    """
    Enum for navigation actions within the bot.
    """

    START = "start"  # Command to start the bot.
    MAIN_MENU = "main_menu"  # Navigate to main menu.
    REFERRAL = "referral"  # Navigate to referral system.
    PROMOCODE = "promocode"  # Navigate to activate promocode.

    # region: Profile
    PROFILE = "profile"
    SHOW_KEY = "show_key"

    # region: Admin tools
    ADMIN_TOOLS = "admin_tools"
    STATISTICS = "statistics"
    EDITOR_USERS = "editor_users"
    EDITOR_PROMOCODES = "editor_promocodes"
    SEND_NOTIFICATION = "send_notification"
    CREATE_BACKUP = "create_backup"
    RESTART_BOT = "restart_bot"
    # endregion

    # region: Editor Promocodes
    CREATE_PROMOCODE = "create_promocode"
    DELETE_PROMOCODE = "delete_promocode"
    EDIT_PROMOCODE = "edit_promocode"
    # endregion

    # region: Subscribtion
    SUBSCRIPTION = "subscription"
    PROCESS = "process"
    TRAFFIC = "traffic"
    DURATION = "duration"
    BACK_TO_DURATION = "back_to_duration"
    BACK_TO_PAYMENT = "back_to_payment"
    PAY = "pay"
    PAY_YOOKASSA = f"{PAY}_yookassa"
    PAY_TELEGRAM_STARS = f"{PAY}_telegram_stars"
    PAY_CRYPTOMUS = f"{PAY}_cryptomus"
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


class States(Enum):
    TRAFFIC = "traffic"
    DURATION = "duration"
    PAY = "pay"
    PAY_YOOKASSA = f"{PAY}_yookassa"
    PAY_TELEGRAM_STARS = f"{PAY}_telegram_stars"
    PAY_CRYPTOMUS = f"{PAY}_cryptomus"


class SubscriptionCallback(CallbackData, prefix="subscription"):
    state: States
    traffic: int = 0
    duration: int = 0
    price: int = 0


class PromocodeCallback(CallbackData, prefix="create_promocode"):
    state: States
    traffic: int = 0
    duration: int = 0
