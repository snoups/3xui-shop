from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button, back_to_main_menu_button
from app.bot.navigation import Navigation, SubscriptionCallback
from app.bot.services.plans import PlansService


def pay_keyboard(pay_url: str, callback_data: SubscriptionCallback) -> InlineKeyboardMarkup:
    """
    Generates a payment keyboard with a link to the payment URL and a back button.

    This keyboard is designed for users to initiate a payment. It includes a button
    with the specified payment URL and a back button to navigate to the duration selection menu.

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

    This keyboard provides a button for the user to download the app after completing
    the payment process, along with a back button that redirects the user to the main menu.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with a download button and a back button to main menu.
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
