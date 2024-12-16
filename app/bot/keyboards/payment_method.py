from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction
from app.bot.services.subscription import SubscriptionService


def payment_method_keyboard(
    prices: dict,
    duration: int,
    subscription: SubscriptionService,
) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting a payment method.

    This keyboard includes options for different payment methods
    and a button to navigate back to the duration selection step.

    Arguments:
        prices (dict): A dictionary of prices for various payment methods.
        duration (int): The selected duration of the subscription in days.
        subscription (SubscriptionService): Service for retrieving price information.

    Returns:
        InlineKeyboardMarkup: An inline keyboard with payment method options and a back button.
    """
    builder = InlineKeyboardBuilder()

    price = subscription.get_price_for_duration(prices, duration, "RUB")
    builder.row(
        InlineKeyboardButton(
            text=_("YooKassa | {price} ₽").format(price=price),
            callback_data=NavigationAction.PAY_YOOKASSA,
        )
    )

    price = subscription.get_price_for_duration(prices, duration, "XTR")
    builder.row(
        InlineKeyboardButton(
            text="TelegramStars | {price} ★".format(price=price),
            callback_data=NavigationAction.PAY_TELEGRAM_STARS,
        )
    )

    price = subscription.get_price_for_duration(prices, duration, "USD")
    builder.row(
        InlineKeyboardButton(
            text="Cryptomus | {price} $".format(price=price),
            callback_data=NavigationAction.PAY_CRYPTOMUS,
        )
    )

    builder.row(back_button(NavigationAction.BACK_TO_DURATION))
    return builder.as_markup()
