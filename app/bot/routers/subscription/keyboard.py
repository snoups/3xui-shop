from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.bot.services import PlanService

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.models import SubscriptionData
from app.bot.payment_gateways import PaymentGateway
from app.bot.routers.misc.keyboard import back_button, back_to_main_menu_button
from app.bot.utils.navigation import NavDownload, NavSubscription


def change_subscription_button() -> InlineKeyboardButton:
    return InlineKeyboardButton(
        text=_("subscription:button:change"),
        callback_data=NavSubscription.CHANGE,
    )


def subscription_keyboard(
    has_subscription: bool,
    callback_data: SubscriptionData,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    if not has_subscription:
        builder.button(
            text=_("subscription:button:buy"),
            callback_data=callback_data,
        )
    else:
        callback_data.state = NavSubscription.EXTEND
        builder.button(
            text=_("subscription:button:extend"),
            callback_data=callback_data,
        )

    builder.button(
        text=_("subscription:button:activate_promocode"),
        callback_data=NavSubscription.PROMOCODE,
    )
    builder.adjust(1)
    builder.row(back_to_main_menu_button())
    return builder.as_markup()


def devices_keyboard(
    plan_service: PlanService,
    callback_data: SubscriptionData,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    plans = plan_service.plans

    for plan in plans:
        callback_data.devices = plan.devices
        builder.button(
            text=plan_service.convert_devices_to_title(plan.devices),
            callback_data=callback_data,
        )

    builder.adjust(2)
    builder.row(back_button(NavSubscription.MAIN))
    return builder.as_markup()


def duration_keyboard(
    plan_service: PlanService,
    callback_data: SubscriptionData,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    durations = plan_service.durations

    for duration in durations:
        callback_data.duration = duration
        period = plan_service.convert_days_to_period(duration)
        price = plan_service.get_plan(callback_data.devices).prices.rub[duration]
        builder.button(
            text=f"{period} | {price} ₽",  # TODO: set default currency in config
            callback_data=callback_data,
        )

    builder.adjust(2)

    if callback_data.is_extend:
        builder.row(back_button(NavSubscription.MAIN))
    else:
        callback_data.state = NavSubscription.PROCESS
        builder.row(back_button(callback_data.pack()))

    return builder.as_markup()


def pay_keyboard(pay_url: str, callback_data: SubscriptionData) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(InlineKeyboardButton(text=_("subscription:button:pay"), url=pay_url))

    callback_data.state = NavSubscription.DURATION
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()


def payment_method_keyboard(
    gateways: dict[str, PaymentGateway],
    callback_data: SubscriptionData,
    plan_service: PlanService,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    plan = plan_service.get_plan(callback_data.devices)

    for gateway_name, gateway in gateways.items():
        price = plan.prices.to_dict()[gateway.code][str(callback_data.duration)]
        if price is None:
            continue

        callback_data.state = gateway.callback
        builder.row(
            InlineKeyboardButton(
                text=f"{_(gateway.name)} | {price} {gateway.symbol}",
                callback_data=callback_data.pack(),
            )
        )

    callback_data.state = NavSubscription.DEVICES
    builder.row(back_button(callback_data.pack()))
    return builder.as_markup()


def payment_success_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    builder.row(
        InlineKeyboardButton(
            text=_("subscription:button:download_app"),
            callback_data=NavDownload.MAIN,
        )
    )

    builder.row(back_to_main_menu_button())
    return builder.as_markup()
