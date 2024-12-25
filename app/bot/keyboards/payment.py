from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button, back_to_main_menu_button
from app.bot.navigation import Navigation, SubscriptionCallback
from app.bot.services.plans import PlansService


def pay_keyboard(pay_url: str, callback_data: SubscriptionCallback) -> InlineKeyboardMarkup:
    """
    Generates a payment keyboard with a link to the payment URL and a back button.

    Arguments:
        pay_url (str): URL to redirect the user to the payment page.
        callback_data (SubscriptionCallback): Callback data to identify the navigation state.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with a pay button and a back button.
    """
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_("💸 Pay"), url=pay_url))

    callback_data.state = Navigation.DURATION
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()


def payment_method_keyboard(
    callback_data: SubscriptionCallback,
    plans_service: PlansService,
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for choosing a payment method.

    Arguments:
        callback_data (SubscriptionCallback): Data used to track user navigation and selections.
        plans_service (PlansService): Service providing subscription plans.

    Returns:
        InlineKeyboardMarkup: A keyboard with buttons for each payment method.
    """
    builder = InlineKeyboardBuilder()
    plan = plans_service.get_plan(callback_data.devices)

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

    callback_data.state = Navigation.DEVICES
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()


def payment_success_keyboard() -> InlineKeyboardMarkup:
    """
    Generates a keyboard for the successful payment confirmation.

    Provides a button to download the app after payment, with a back button to the main menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with download and back-to-main-menu buttons.
    """
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("📥 Download app"),
            callback_data=Navigation.DOWNLOAD,
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()
