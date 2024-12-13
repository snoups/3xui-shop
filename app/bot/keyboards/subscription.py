from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction
from app.bot.services import subscription_service


def traffic_keyboard() -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting a subscription plan by traffic volume.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup with traffic options and a back button.
    """
    builder = InlineKeyboardBuilder()
    plans = subscription_service.plans

    for plan in plans:
        traffic = subscription_service.convert_traffic_to_title(plan["traffic"])
        callback_data = subscription_service.generate_plan_callback(plan["traffic"])
        builder.row(
            InlineKeyboardButton(
                text=traffic,
                callback_data=callback_data,
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def duration_keyboard(prices: dict) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting subscription duration with calculated prices.

    Arguments:
        price (float): Base price of the subscription.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup with duration options and a back button.
    """
    builder = InlineKeyboardBuilder()
    durations = subscription_service.durations

    for duration in durations:
        period = subscription_service.convert_days_to_period(duration)
        price = subscription_service.get_price_for_duration(prices, duration)
        callback_data = subscription_service.generate_duration_callback(duration)
        builder.row(
            InlineKeyboardButton(
                text=f"{period} | {price} ₽",
                callback_data=callback_data,
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavigationAction.SUBSCRIPTION))
    return builder.as_markup()
