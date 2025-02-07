import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsDev
from app.bot.models import ServicesContainer, SubscriptionData, TransactionStatus
from app.bot.routers.misc.keyboard import back_keyboard
from app.bot.utils.constants import MAIN_MESSAGE_ID_KEY
from app.bot.utils.navigation import NavSubscription
from app.db.models import Server, Transaction, User

from .keyboard import pay_keyboard, payment_success_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(SubscriptionData.filter(F.state.startswith(NavSubscription.PAY)))
async def callback_payment_method_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    services: ServicesContainer,
    bot: Bot,
) -> None:
    # TODO: FIX MANY CALL
    method = callback_data.state
    devices = callback_data.devices
    duration = callback_data.duration
    logger.info(f"User {user.tg_id} selected payment method: {method}")
    logger.info(f"User {user.tg_id} selected {devices} devices and {duration} days.")
    gateway = services.payment.get_gateway(method)
    price = services.plan.get_price_for_duration(
        services.plan.get_plan(devices).prices.to_dict(),
        duration,
        gateway.code,
    )
    callback_data.price = price

    # TODO: Make a check for the existence of a subscription

    pay_url = await services.payment.create_payment(gateway, callback_data)
    logger.info(f"Payment link created for user {user.tg_id}: {pay_url}")

    text = _("payment:message:order").format(
        devices=devices,
        duration=services.plan.convert_days_to_period(duration),
        price=price,
        currency=gateway.symbol,
    )
    await callback.message.edit_text(text, reply_markup=pay_keyboard(pay_url, callback_data))


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, user: User) -> None:
    logger.info(f"Pre-checkout query received from user {user.tg_id}")
    if pre_checkout_query.invoice_payload:
        await pre_checkout_query.answer(ok=True)
    else:
        await pre_checkout_query.answer(ok=False)


@router.message(F.successful_payment)
async def successful_payment(
    message: Message,
    user: User,
    session: AsyncSession,
    bot: Bot,
    state: FSMContext,
    services: ServicesContainer,
) -> None:
    logger.info(f"Payment successful for user {user.tg_id}")
    await state.update_data(callback=NavSubscription.MAIN)
    data = SubscriptionData.unpack(message.successful_payment.invoice_payload)
    logger.debug(f"Subscription data unpacked: {data}")

    if await IsDev()(message):
        await bot.refund_star_payment(
            user_id=user.tg_id,
            telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
        )

    message_id = await state.get_value(MAIN_MESSAGE_ID_KEY)
    try:
        await bot.delete_message(chat_id=user.tg_id, message_id=message_id)
    except Exception as exception:
        logger.debug(f"Failed to delete message: {exception}")

    # server = await Server.get_available(session)
    # await User.update(session, user.tg_id, server_id=server.id)  # TODO: create method
    # await session.refresh(user, ["server"])

    if data.is_extend:
        await services.vpn.extend_subscription(user, data.devices, data.duration)
        logger.info(f"Subscription extented for user {user.tg_id}")
    else:
        await services.vpn.create_subscription(user, data.devices, data.duration)
        logger.info(f"Subscription created for user {user.tg_id}")

    await Transaction.create(
        session=session,
        tg_id=user.tg_id,
        subscription=data.pack(),
        payment_id=message.successful_payment.telegram_payment_charge_id,
        status=TransactionStatus.COMPLETED,
    )

    if data.is_extend:
        await message.answer(
            text=_("payment:message:extend_success").format(
                duration=services.plan.convert_days_to_period(data.duration)
            ),
            message_effect_id="5046509860389126442",
            reply_markup=back_keyboard(NavSubscription.MAIN),
        )
    else:
        key = await services.vpn.get_key(user)
        await message.answer(
            text=_("payment:message:buying_success").format(key=key),
            message_effect_id="5046509860389126442",  # TODO: Delete effect
            reply_markup=payment_success_keyboard(),
        )
