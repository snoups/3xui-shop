from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction
from app.bot.services import subscription_service


def payment_method_keyboard(prices: dict, duration: int) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting a payment method based on the subscription plan.

    Arguments:
        plan (dict): Subscription plan details, including prices for various payment methods.
        coefficient (int): Price adjustment coefficient for the subscription plan.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup with payment method options and a back button.
    """
    builder = InlineKeyboardBuilder()

    # TODO: Checking initialization of payment gateways
    yookassa = True
    telegram_stars = True
    cryptomus = True

    if yookassa:
        price = subscription_service.get_price_for_duration(prices, duration, "RUB")
        builder.row(
            InlineKeyboardButton(
                text=_("YooKassa | {price} ₽").format(price=price),
                callback_data=NavigationAction.PAY_YOOKASSA,
            )
        )

    if telegram_stars:
        price = subscription_service.get_price_for_duration(prices, duration, "XTR")
        builder.row(
            InlineKeyboardButton(
                text="TelegramStars | {price} ★".format(price=price),
                callback_data=NavigationAction.PAY_TELEGRAM_STARS,
            )
        )

    if cryptomus:
        price = subscription_service.get_price_for_duration(prices, duration, "USD")
        builder.row(
            InlineKeyboardButton(
                text="Cryptomus | {price} $".format(price=price),
                callback_data=NavigationAction.PAY_CRYPTOMUS,
            )
        )

    builder.row(back_button(NavigationAction.BACK_TO_DURATION))
    return builder.as_markup()
