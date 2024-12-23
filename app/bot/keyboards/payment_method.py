from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import Navigation, SubscriptionCallback
from app.bot.services.plans import PlansService


def payment_method_keyboard(
    callback_data: SubscriptionCallback,
    plans_service: PlansService,
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for choosing a payment method.

    The keyboard includes options for selecting a payment method, such as YooKassa,
    TelegramStars, and Cryptomus. The prices are dynamically fetched from the subscription
    service based on the selected traffic amount and duration.

    Arguments:
        callback_data (SubscriptionCallback): Data used to track user navigation and selections.
        plans_service (PlansService): Service providing subscription plans.

    Returns:
        InlineKeyboardMarkup: A keyboard with buttons for each payment method,
        along with a back button to return to the previous menu.
    """
    builder = InlineKeyboardBuilder()
    plan = plans_service.get_plan(callback_data.traffic)

    callback_data.state = Navigation.PAY_YOOKASSA
    price = plan.prices.rub[callback_data.duration]
    builder.row(
        InlineKeyboardButton(
            text=_("YooKassa | {price} ₽").format(price=price),
            callback_data=callback_data.pack(),
        )
    )
    callback_data.state = Navigation.PAY_TELEGRAM_STARS
    price = plan.prices.xtr[callback_data.duration]
    builder.row(
        InlineKeyboardButton(
            text="TelegramStars | {price} ★".format(price=price),
            callback_data=callback_data.pack(),
        )
    )
    callback_data.state = Navigation.PAY_CRYPTOMUS
    price = plan.prices.usd[callback_data.duration]
    builder.row(
        InlineKeyboardButton(
            text="Cryptomus | {price} $".format(price=price),
            callback_data=callback_data.pack(),
        )
    )

    callback_data.state = Navigation.TRAFFIC
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()
