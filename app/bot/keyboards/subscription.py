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

    If the user doesn't have an active subscription, a button to purchase one is displayed.
    Additionally, all users have access to a promocode activation button and a main menu button.

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
    plans_service: PlansService,
    callback_data: SubscriptionCallback,
) -> InlineKeyboardMarkup:
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


def traffic_keyboard(
    plans_service: PlansService,
    callback_data: SubscriptionCallback,
) -> InlineKeyboardMarkup:
    """
    Generates a keyboard for selecting a traffic plan during subscription purchase.

    Displays traffic options based on the available plans from the subscription service.
    Each button updates the callback data with the selected traffic amount.

    Arguments:
        plans_service (PlansService): Service providing subscription plans.
        callback_data (SubscriptionCallback): Data to track the user's navigation and selections.

    Returns:
        InlineKeyboardMarkup: Keyboard with traffic plan options and a back button.
    """
    builder = InlineKeyboardBuilder()
    plans = plans_service.plans

    for plan in plans:
        callback_data.traffic = plan.traffic
        traffic = plans_service.convert_traffic_to_title(plan.traffic)
        builder.row(
            InlineKeyboardButton(
                text=traffic,
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
    Generates a keyboard for selecting the subscription duration.

    Options include various duration periods, with dynamically fetched prices based on the
    selected traffic plan. Buttons update the callback data with the chosen duration.

    Arguments:
        plans_service (PlansService): Service providing subscription plans and prices.
        callback_data (SubscriptionCallback): Data to track the user's navigation and selections.

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
