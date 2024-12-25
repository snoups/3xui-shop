import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _

from app.bot.filters import IsPrivate
from app.bot.keyboards.payment import payment_method_keyboard
from app.bot.keyboards.subscription import (
    duration_keyboard,
    subscription_keyboard,
    traffic_keyboard,
)
from app.bot.navigation import Navigation, SubscriptionCallback
from app.bot.services.client import ClientService
from app.bot.services.plans import PlansService
from app.bot.services.vpn import VPNService

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_subscription(
    callback: CallbackQuery,
    client_service: ClientService,
    callback_data: SubscriptionCallback,
) -> None:
    """
    Prepares and shows the subscription status message for the user.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        client_service (ClientService): Service for managing client subscriptions and data.
        callback_data (SubscriptionCallback): The data related to the subscription callback.
    """
    text = ""
    if client_service:
        if client_service.has_subscription_expired and client_service.has_traffic_expired:
            text = _("⚠️ *Your subscription period and traffic have expired!*\n")
        elif client_service.has_traffic_expired:
            text = _("⚠️ *Traffic limit reached!*\n")
        elif client_service.has_subscription_expired:
            text = _("⚠️ *Subscription period has expired!*\n")
        text += "\n" + _("Please renew your subscription to continue using our service.")

        if client_service.has_valid_subscription:
            text = _(
                "✅ *You already have an active subscription:*\n"
                "\n"
                "Plan: {plan}\n"
                "Remaining Traffic: {traffic}\n"
                "Expires on: {expiry_time}"
            ).format(
                plan=client_service.traffic_total,
                traffic=client_service.traffic_remaining,
                expiry_time=client_service.expiry_time,
            )
    else:
        text = _(
            "⚠️ *You do not have an active subscription!*\n"
            "\n"
            "It seems that you haven't purchased a subscription yet. "
            "Please buy a subscription to start using our service."
        )

    await callback.message.edit_text(
        text=text, reply_markup=subscription_keyboard(client_service, callback_data)
    )  # TODO: Make subscription renewals and changes possible


@router.callback_query(F.data == Navigation.SUBSCRIPTION, IsPrivate())
async def callback_subscription(callback: CallbackQuery, vpn_service: VPNService) -> None:
    """
    Handler for opening the subscription page.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        vpn_service (VPNService): Service for managing VPN subscriptions and retrieving client data.
    """
    logger.info(f"User {callback.from_user.id} opened subscription.")
    client_data = await vpn_service.get_client_data(callback.from_user.id)
    client_service = ClientService(client_data)
    callback_data = SubscriptionCallback(state=Navigation.PROCESS, user_id=callback.from_user.id)
    await show_subscription(callback, client_service, callback_data)


@router.callback_query(SubscriptionCallback.filter(F.state == Navigation.PROCESS), IsPrivate())
async def callback_subscription_process(
    callback: CallbackQuery,
    callback_data: SubscriptionCallback,
    plans_service: PlansService,
):
    """
    Handler for starting the subscription process by selecting traffic.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        callback_data (SubscriptionCallback): The data related to the subscription callback.
        plans_service (PlansService): Service for retrieving available plans and prices.
    """
    logger.info(f"User {callback.from_user.id} started subscription process.")
    callback_data.state = Navigation.TRAFFIC
    text = _("🌐 *Select the traffic volume:*")
    await callback.message.edit_text(
        text=text, reply_markup=traffic_keyboard(plans_service, callback_data)
    )


@router.callback_query(SubscriptionCallback.filter(F.state == Navigation.TRAFFIC), IsPrivate())
async def callback_traffic_selected(
    callback: CallbackQuery,
    callback_data: SubscriptionCallback,
    plans_service: PlansService,
) -> None:
    """
    Handler for selecting the traffic volume during subscription.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        callback_data (SubscriptionCallback): The data related to the subscription callback.
        plans_service (PlansService): Service for retrieving available plans and prices.
    """
    logger.info(f"User {callback.from_user.id} selected traffic: {callback_data.traffic}")
    callback_data.state = Navigation.DURATION
    await callback.message.edit_text(
        text=_("⏳ *Specify the duration:*"),
        reply_markup=duration_keyboard(plans_service, callback_data),
    )


@router.callback_query(SubscriptionCallback.filter(F.state == Navigation.DURATION), IsPrivate())
async def callback_duration_selected(
    callback: CallbackQuery,
    callback_data: SubscriptionCallback,
    plans_service: PlansService,
) -> None:
    """
    Handler for selecting the subscription duration.

    Arguments:
        callback (CallbackQuery): The callback query object containing user interaction.
        callback_data (SubscriptionCallback): The data related to the subscription callback.
        plans_service (PlansService): Service for retrieving available plans and prices.
    """
    logger.info(f"User {callback.from_user.id} selected duration: {callback_data.duration}")
    callback_data.state = Navigation.PAY
    await callback.message.edit_text(
        text=_("💳 *Choose a payment method:*"),
        reply_markup=payment_method_keyboard(callback_data, plans_service),
    )
