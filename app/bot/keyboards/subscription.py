from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button
from app.bot.navigation import NavigationAction
from app.bot.services.subscription import SubscriptionService


def traffic_keyboard(subscription: SubscriptionService) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting a subscription plan based on traffic volume.

    This keyboard allows the user to choose a subscription plan based on traffic (in GB).
    It generates callback data for each plan and includes a back button to return to the main menu.

    Arguments:
        subscription (SubscriptionService): The service used to fetch subscription plans.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup with traffic options and a back button.
    """
    builder = InlineKeyboardBuilder()
    plans = subscription.plans

    for plan in plans:
        traffic = subscription.convert_traffic_to_title(plan["traffic"])
        callback_data = subscription.generate_plan_callback(plan["traffic"])
        builder.row(
            InlineKeyboardButton(
                text=traffic,
                callback_data=callback_data,
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def duration_keyboard(prices: dict, subscription: SubscriptionService) -> InlineKeyboardMarkup:
    """
    Generates an inline keyboard for selecting the subscription duration with calculated prices.

    This keyboard displays the available subscription durations, along with the price for each
    duration based on the selected traffic plan. It also includes a back button to return to
    the subscription selection.

    Args:
        prices (dict): A dictionary containing the prices for various payment methods.
        subscription (SubscriptionService): The service used to fetch subscription durations.

    Returns:
        InlineKeyboardMarkup: The inline keyboard markup with duration options and a back button.
    """
    builder = InlineKeyboardBuilder()
    durations = subscription.durations

    for duration in durations:
        period = subscription.convert_days_to_period(duration)
        price = subscription.get_price_for_duration(prices, duration)
        callback_data = subscription.generate_duration_callback(duration)
        builder.row(
            InlineKeyboardButton(
                text=f"{period} | {price} ₽",
                callback_data=callback_data,
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavigationAction.SUBSCRIPTION))
    return builder.as_markup()
