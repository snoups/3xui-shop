from enum import Enum


class NavigationAction(str, Enum):
    """
    Enum for navigation actions within the bot.
    """

    START = "start"  # Command to start the bot.
    MAIN_MENU = "main_menu"  # Navigate to main menu.
    PROFILE = "profile"  # Navigate to user profile.

    # Navigation on Subscribtion/Payment page
    SUBSCRIPTION = "subscription"
    EXTEND = "extend"
    TRAFFIC = "traffic"
    DURATION = "duration"
    BACK_TO_DURATION = "back_to_duration"
    BACK_TO_PAYMENT = "back_to_payment"
    PAY = "pay"
    PAY_YOOKASSA = f"{PAY}_yookassa"
    PAY_TELEGRAM_STARS = f"{PAY}_telegram_stars"
    PAY_CRYPTOMUS = f"{PAY}_cryptomus"

    REFERAL = "referal"  # Navigate to referral system.
    PROMOCODE = "promocode"  # Navigate to activate promocode.

    # Navigation on Download page
    DOWNLOAD = "download"
    PLATFORM = "platform"
    PLATFORM_IOS = f"{PLATFORM}_ios"
    PLATFORM_ANDROID = f"{PLATFORM}_android"
    PLATFORM_WINDOWS = f"{PLATFORM}_windows"

    # Navigation on Support page
    SUPPORT = "support"
    HOW_TO_CONNECT = "how_to_connect"
    VPN_NOT_WORKING = "vpn_not_working"
