from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.keyboards.back import back_button, back_to_main_menu_button
from app.bot.navigation import Navigation, SubscriptionCallback
from app.bot.services.plans import PlansService


def renew_subscription_button() -> InlineKeyboardButton:
    """
    Generates a button for renewing the user's subscription.

    Returns:
        InlineKeyboardButton: Button to renew the subscription.
    """
    return InlineKeyboardButton(text=_("💳 Renew subscription"), callback_data=Navigation.PROCESS)


def subscription_keyboard(
    has_subscription: bool, callback_data: SubscriptionCallback
) -> InlineKeyboardMarkup:
    """
    Generates a subscription keyboard with options based on the user's subscription status.

    Displays a button to buy a subscription if not active, a promocode activation button,
    and a back button.

    Arguments:
        has_subscription (bool): Indicates whether the user has an active subscription.
        callback_data (SubscriptionCallback): Data for tracking the user's navigation state.

    Returns:
        InlineKeyboardMarkup: Keyboard with subscription management options.
    """
    builder = InlineKeyboardBuilder()

    if not has_subscription:
        builder.row(
            InlineKeyboardButton(
                text=_("💳 Buy subscription"),
                callback_data=callback_data.pack(),
            )
        )

    builder.row(
        InlineKeyboardButton(
            text=_("🎟️ Activate promocode"),
            callback_data=Navigation.PROMOCODE,
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def devices_keyboard(
    plans_service: PlansService, callback_data: SubscriptionCallback
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard to select subscription devices.

    Displays a row of device options based on available plans, each updating the callback data.

    Arguments:
        plans_service (PlansService): Service providing available plans.
        callback_data (SubscriptionCallback): Data for tracking the user's selection.

    Returns:
        InlineKeyboardMarkup: Keyboard with device options and a back button.
    """
    builder = InlineKeyboardBuilder()
    plans = plans_service.plans

    for plan in plans:
        callback_data.devices = plan.devices
        builder.row(
            InlineKeyboardButton(
                text=plans_service.convert_devices_to_title(plan.devices),
                callback_data=callback_data.pack(),
            )
        )

    builder.adjust(2)
    builder.row(back_button(Navigation.SUBSCRIPTION))
    return builder.as_markup()


def duration_keyboard(
    plans_service: PlansService,
    callback_data: SubscriptionCallback,
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for selecting subscription duration.

    Options include various durations with dynamically fetched prices based on selected devices.

    Arguments:
        plans_service (PlansService): Service providing subscription plans and prices.
        callback_data (SubscriptionCallback): Data to track the user's selections.

    Returns:
        InlineKeyboardMarkup: Keyboard with duration options and a back button.
    """
    builder = InlineKeyboardBuilder()
    durations = plans_service.durations

    for duration in durations:
        callback_data.duration = duration
        period = plans_service.convert_days_to_period(duration)
        price = plans_service.get_plan(callback_data.devices).prices.rub[duration]
        builder.row(
            InlineKeyboardButton(
                text=f"{period} | {price} ₽",
                callback_data=callback_data.pack(),
            )
        )

    builder.adjust(2)
    callback_data.state = Navigation.PROCESS
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()
