import logging

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.models import ClientData, ServicesContainer, SubscriptionData
from app.bot.payment_gateways import GatewayFactory
from app.bot.utils.navigation import NavSubscription
from app.config import Config
from app.db.models import Server, User

from .keyboard import (
    devices_keyboard,
    duration_keyboard,
    payment_method_keyboard,
    subscription_keyboard,
    payment_success_keyboard,
)

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def show_subscription(
    callback: CallbackQuery,
    client_data: ClientData | None,
    callback_data: SubscriptionData,
    config: Config,
    user: User,
) -> None:
    if client_data:
        if client_data.has_subscription_expired:
            text = _("subscription:message:expired")
        else:
            text = _("subscription:message:active").format(
                devices=client_data.max_devices,
                expiry_time=client_data.expiry_time,
            )
    else:
        text = _("subscription:message:not_active")

    await callback.message.edit_text(
        text=text,
        reply_markup=subscription_keyboard(
            has_subscription=client_data,
            callback_data=callback_data,
            config=config,
            user=user,
        ),
    )


@router.callback_query(F.data == NavSubscription.MAIN)
async def callback_subscription(
    callback: CallbackQuery,
    user: User,
    state: FSMContext,
    services: ServicesContainer,
    config: Config,
) -> None:
    logger.info(f"User {user.tg_id} opened subscription page.")
    await state.set_state(None)

    client_data = None
    if user.server_id:
        client_data = await services.vpn.get_client_data(user)
        if not client_data:
            await services.notification.show_popup(
                callback=callback,
                text=_("subscription:popup:error_fetching_data"),
            )

    callback_data = SubscriptionData(state=NavSubscription.PROCESS, user_id=user.tg_id)
    await show_subscription(
        callback=callback,
        client_data=client_data,
        callback_data=callback_data,
        config=config,
        user=user,
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.EXTEND))
async def callback_subscription_extend(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started extend subscription.")
    client = await services.vpn.is_client_exists(user)
    callback_data.devices = await services.vpn.get_limit_ip(user=user, client=client)
    callback_data.state = NavSubscription.DURATION
    callback_data.is_extend = True
    await callback.message.edit_text(
        text=_("subscription:message:duration"),
        reply_markup=duration_keyboard(
            plan_service=services.plan,
            callback_data=callback_data,
            currency=config.shop.CURRENCY,
        ),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.CHANGE))
async def callback_subscription_change(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started change subscription.")
    callback_data.state = NavSubscription.DEVICES
    callback_data.is_change = True
    await callback.message.edit_text(
        text=_("subscription:message:devices"),
        reply_markup=devices_keyboard(services.plan.get_all_plans(), callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.PROCESS))
async def callback_subscription_process(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    callback_data: SubscriptionData,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} started subscription process.")
    server = await services.server_pool.get_available_server()

    if not server:
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:no_available_servers"),
            cache_time=120,
        )
        return

    callback_data.state = NavSubscription.DEVICES
    await callback.message.edit_text(
        text=_("subscription:message:devices"),
        reply_markup=devices_keyboard(services.plan.get_all_plans(), callback_data),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DEVICES))
async def callback_devices_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    config: Config,
    services: ServicesContainer,
) -> None:
    logger.info(f"User {user.tg_id} selected devices: {callback_data.devices}")
    callback_data.state = NavSubscription.DURATION
    await callback.message.edit_text(
        text=_("subscription:message:duration"),
        reply_markup=duration_keyboard(
            plan_service=services.plan,
            callback_data=callback_data,
            currency=config.shop.CURRENCY,
        ),
    )


@router.callback_query(SubscriptionData.filter(F.state == NavSubscription.DURATION))
async def callback_duration_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
    gateway_factory: GatewayFactory,
) -> None:
    logger.info(f"User {user.tg_id} selected duration: {callback_data.duration}")
    callback_data.state = NavSubscription.PAY
    await callback.message.edit_text(
        text=_("subscription:message:payment_method"),
        reply_markup=payment_method_keyboard(
            plan=services.plan.get_plan(callback_data.devices),
            callback_data=callback_data,
            gateways=gateway_factory.get_gateways(),
        ),
    )


@router.callback_query(F.data == NavSubscription.TRIAL)
async def callback_trial_subscription(
    callback: CallbackQuery,
    user: User,
    session: AsyncSession,
    config: Config,
    services: ServicesContainer,
    state: FSMContext,
) -> None:
    logger.info(f"User {user.tg_id} started trial subscription.")
    
    if user.trial_used:
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:trial_already_used"),
            cache_time=120,
        )
        return

    server = await services.server_pool.get_available_server()

    if not server:
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:no_available_servers"),
            cache_time=120,
        )
        return

    success = await services.vpn.create_subscription(
        user=user,
        devices=1,
        duration=config.shop.TRIAL_PERIOD,
    )

    if success:
        await User.update(
            session=session,
            tg_id=user.tg_id,
            trial_used=True,
        )
        key = await services.vpn.get_key(user)
        await services.notification.notify_trial_success(
            user_id=user.tg_id,
            key=key,
        )
        # Перенаправляем на главную страницу
        from app.bot.routers.main_menu.handler import redirect_to_main_menu
        await redirect_to_main_menu(
            bot=callback.bot,
            user=user,
            state=state,
        )
    else:
        await services.notification.show_popup(
            callback=callback,
            text=_("subscription:popup:error_creating_subscription"),
            cache_time=120,
        )
