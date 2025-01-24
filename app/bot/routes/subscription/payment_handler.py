import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsDev
from app.bot.navigation import NavSubscription, SubscriptionData
from app.bot.routes.utils.keyboard import back_to_main_menu_keyboard
from app.bot.services import PaymentService, PlanService, VPNService
from app.db.models import Transaction, User

from .keyboard import pay_keyboard, payment_success_keyboard

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(SubscriptionData.filter(F.state.startswith(NavSubscription.PAY)))
async def callback_payment_method_selected(
    callback: CallbackQuery,
    user: User,
    callback_data: SubscriptionData,
    plan_service: PlanService,
    payment_service: PaymentService,
    session: AsyncSession,
    bot: Bot,
) -> None:
    # TODO: FIX MANY CALL
    method = callback_data.state
    devices = callback_data.devices
    duration = callback_data.duration
    logger.info(f"User {user.tg_id} selected payment method: {method}")
    logger.info(f"User {user.tg_id} selected {devices} devices and {duration} days.")
    gateway = payment_service.get_gateway(method)
    price = plan_service.get_price_for_duration(
        plan_service.get_plan(devices).prices.to_dict(),
        duration,
        gateway.code,
    )
    callback_data.price = price
    callback_data.message_id = callback.message.message_id

    # TODO: Make a check for the existence of a subscription

    # await Transaction.create(
    #     session=session,
    #     user_id=callback.from_user.id,
    #     payment_id=,
    #     amount=price,
    #     status="process",
    # )

    link = await payment_service.create_payment(gateway, callback_data, bot)
    logger.info(f"Payment link created for user {user.tg_id}: {link}")

    await callback.message.edit_text(
        text=_(
            "✅ *You selected:*\n"
            "\n"
            "Devices: {devices}\n"
            "Duration: {duration}\n"
            "Price: {price} {currency}\n"
            "\n"
            "_After payment, a unique key will be generated for you, to connect to the VPN. "
            "The key will be available in your profile._"
        ).format(
            devices=devices,
            duration=plan_service.convert_days_to_period(duration),
            price=price,
            currency=gateway.symbol,
        ),
        reply_markup=pay_keyboard(link, callback_data),
    )


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery, user: User) -> None:
    logger.info(f"Pre-checkout query received from user {user.tg_id}")
    if pre_checkout_query.invoice_payload is not None:
        await pre_checkout_query.answer(ok=True)
    else:
        await pre_checkout_query.answer(ok=False)  # TODO: FIX never


@router.message(F.successful_payment)
async def successful_payment(
    message: Message,
    user: User,
    session: AsyncSession,
    vpn_service: VPNService,
    bot: Bot,
    state: FSMContext,
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

    await bot.delete_message(chat_id=user.tg_id, message_id=data.message_id)
    # await bot.edit_message_text(
    #     text="Successful payment!",
    #     chat_id=user.tg_id,
    #     message_id=data.message_id,
    #     reply_markup=back_to_main_menu_keyboard(),
    # )

    if data.is_extend:
        await vpn_service.extend_subscription(user.tg_id, data.devices, data.duration)
        logger.info(f"Subscription extented for user {user.tg_id}")
    else:
        await vpn_service.create_subscription(user.tg_id, data.devices, data.duration)
        logger.info(f"Subscription created for user {user.tg_id}")

    await Transaction.create(
        session=session,
        user_id=user.tg_id,
        subscription=message.successful_payment.invoice_payload,
        payment_id=message.successful_payment.telegram_payment_charge_id,
        status="success",
    )

    if data.is_extend:
        await message.answer(
            text=_(
                "✅ *Payment successful!*\n"
                "\n"
                "Your subscription has been extended for {duration}\n"
            ).format(duration=PlanService.convert_days_to_period(data.duration)),
            message_effect_id="5046509860389126442",
            reply_markup=back_to_main_menu_keyboard(),
        )
    else:
        key = await vpn_service.get_key(user.tg_id)
        await message.answer(
            text=_(
                "✅ *Payment successful!*\n"
                "\n"
                "🔑 *Your key:* ```{key}```\n"
                "_The key will be saved in your profile._\n"
                "\n"
                "To start using our service, go to the download page of the application and "
                "download it for your platform. Then you can manually enter the key or click "
                "`🔌 Connect` and the key will be automatically added to the application."
            ).format(key=key),
            message_effect_id="5046509860389126442",  # TODO: Delete effect
            reply_markup=payment_success_keyboard(),
        )
