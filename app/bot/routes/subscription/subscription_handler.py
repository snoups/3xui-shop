import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.navigation import NavSubscription, SubscriptionData
from app.bot.services import ClientData, PaymentService, PlanService, VPNService
from app.db.models import User

from .keyboard import (
    devices_keyboard,
    duration_keyboard,
    payment_method_keyboard,
    subscription_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_subscription(
    callback: CallbackQuery,
    client_data: ClientData,
    callback_data: SubscriptionData,
) -> None:
    text = ""
    if client_data:
        if client_data.has_subscription_expired:
            text = _(
                "⚠️ *Subscription period has expired!*\n"
                "\n"
                "Please renew your subscription to continue using our service."
            )
        else:
            text = _(
                "✅ *You already have an active subscription:*\n"
                "\n"
                "Devices: {devices}\n"
                "Expires on: {expiry_time}"
            ).format(
                devices=client_data.max_devices,
                expiry_time=client_data.expiry_time,
            )
    else:
        text = _(
            "⚠️ *You do not have an active subscription!*\n"
            "\n"
            "It seems that you haven't purchased a subscription yet. "
            "Please buy a subscription to start using our service."
        )

    await callback.message.edit_text(
        text=text, reply_markup=subscription_keyboard(client_data, callback_data)
    )


@router.callback_query(F.data == NavSubscription.MAIN)
async def callback_subscription(
    callback: CallbackQuery,
    user: User,
    vpn_service: VPNService,
) -> None:
    logger.info(f"User {user.tg_id} opened subscription page.")
    client_data = await vpn_service.get_client_data(user.tg_id)
    callback_data = SubscriptionData(state=NavSubscription.PROCESS, user_id=user.tg_id)
    await show_subscription(callback, client_data, callback_data)


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.EXTEND))
async def callback_subscription_extend(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    plan_service: PlanService,
    vpn_service: VPNService,
) -> None:
    logger.info(f"User {user.tg_id} started extend subscription.")
    client = await vpn_service.is_client_exists(user.tg_id)
    callback_data.devices = await vpn_service.get_limit_ip(client)
    callback_data.state = NavSubscription.DURATION
    callback_data.is_extend = True
    await callback.message.edit_text(
        text=_("⏳ *Specify the duration:*"),
        reply_markup=duration_keyboard(plan_service, callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.PROCESS))
async def callback_subscription_process(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    plan_service: PlanService,
) -> None:
    logger.info(f"User {user.tg_id} started subscription process.")
    callback_data.state = NavSubscription.DEVICES
    await callback.message.edit_text(
        text=_("🌐 *Select the number of devices:*"),
        reply_markup=devices_keyboard(plan_service, callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DEVICES))
async def callback_devices_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    plan_service: PlanService,
) -> None:
    logger.info(f"User {user.tg_id} selected devices: {callback_data.devices}")
    callback_data.state = NavSubscription.DURATION
    await callback.message.edit_text(
        text=_("⏳ *Specify the duration:*"),
        reply_markup=duration_keyboard(plan_service, callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DURATION))
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    plan_service: PlanService,
    payment_service: PaymentService,
) -> None:
    logger.info(f"User {user.tg_id} selected duration: {callback_data.duration}")
    callback_data.state = NavSubscription.PAY
    await callback.message.edit_text(
        text=_("💳 *Choose a payment method:*"),
        reply_markup=payment_method_keyboard(payment_service.gateways, callback_data, plan_service),
    )
