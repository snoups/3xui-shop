from enum import Enum


class NavigationAction(str, Enum):
    """
    Enum for navigation actions within the bot.
    """

    START = "start"  # Command to start the bot.
    MAIN_MENU = "main_menu"  # Navigate to the main menu.

    PROFILE = "profile"  # View the user's profile.

    SUBSCRIPTION = "subscription"  # Start the subscription process.
    TRAFFIC = "traffic"  # Navigate to choosing traffic
    DURATION = "duration"  # Navigate to choosing duration
    BACK_TO_DURATION = "back_to_duration"  # Return to duration selection.
    BACK_TO_PAYMENT = "back_to_payment"  # Return to payment method selection.
    PAY = "pay"  # Initiate the payment process.
    PAY_YOOKASSA = "pay_yookassa"  # Pay via YooKassa.
    PAY_TELEGRAM_STARS = "pay_telegram_stars"  # Pay with Telegram Stars.
    PAY_CRYPTOMUS = "pay_cryptomus"  # Pay via Cryptomus.

    REFERAL = "referal"  # Navigate to referral system.
    PROMOCODE = "promocode"  # Apply a promotional code.
    DOWNLOAD = "download"  # Navigate to download app.
    SUPPORT = "support"  # Contact support.
