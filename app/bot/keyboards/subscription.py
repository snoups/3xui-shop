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
        builder.row(
            InlineKeyboardButton(
                text=plan["traffic"] + " " + _("GB"),
                callback_data=plan["callback"],
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavigationAction.MAIN_MENU))
    return builder.as_markup()


def duration_keyboard(price: float) -> InlineKeyboardMarkup:
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
        period = subscription_service.convert_days_to_period(duration["duration"])
        total_price = subscription_service.calculate_price(price, duration["coefficient"])
        builder.row(
            InlineKeyboardButton(
                text=f"{period} | {total_price} ₽",
                callback_data=duration["callback"],
            )
        )

    builder.adjust(2)
    builder.row(back_button(NavigationAction.SUBSCRIPTION))
    return builder.as_markup()
