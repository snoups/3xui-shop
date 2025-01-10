import logging

from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsDev, IsPrivate
from app.bot.keyboards.back import back_to_main_menu_keyboard
from app.bot.keyboards.payment import pay_keyboard, payment_success_keyboard
from app.bot.navigation import NavSubscription, SubscriptionData
from app.bot.services import PaymentService, PlanService, VPNService
from app.db.models import Transaction

logger = logging.getLogger(__name__)
router = Router(name=__name__)


@router.callback_query(
    SubscriptionData.filter(F.state.startswith(NavSubscription.PAY)), IsPrivate()
)
async def callback_payment_method_selected(
    callback: CallbackQuery,
    callback_data: SubscriptionData,
    plan_service: PlanService,
    payment_service: PaymentService,
    session: AsyncSession,
    bot: Bot,
) -> None:
    """
    Handler for when a user selects a payment method for subscription.

    Arguments:
        callback (CallbackQuery): The callback query object containing user selection.
        callback_data (SubscriptionCallback): The data from the callback query.
        plan_service (PlanService): Service for managing subscription plans.
        bot (Bot): The bot instance to send messages and interact with the user.
    """

    # TODO: FIX MANY CALL
    method = callback_data.state
    devices = callback_data.devices
    duration = callback_data.duration
    logger.info(f"User {callback.from_user.id} selected payment method: {method}")
    logger.info(f"User {callback.from_user.id} selected {devices} devices and {duration} days.")
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
    #     user_id=callback.message.from_user.id,
    #     payment_id=,
    #     amount=price,
    #     status="process",
    # )

    link = await payment_service.create_payment(gateway, callback_data, bot)
    logger.info(f"Payment link created for user {callback.from_user.id}: {link}")

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
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery) -> None:
    """
    Handler for pre-checkout query to validate.

    Arguments:
        pre_checkout_query (PreCheckoutQuery): The pre-checkout query from Telegram.
    """
    logger.info(f"Pre-checkout query received from user {pre_checkout_query.from_user.id}")
    if pre_checkout_query.invoice_payload is not None:
        await pre_checkout_query.answer(ok=True)
    else:
        await pre_checkout_query.answer(ok=False)


@router.message(F.successful_payment)
async def successful_payment(
    message: Message,
    session: AsyncSession,
    vpn_service: VPNService,
    bot: Bot,
) -> None:
    """
    Handler for successful payment. Creates or extends the subscription.

    Arguments:
        message (Message): The message object containing payment success details.
        session (AsyncSession): The session for interacting with the database.
        vpn_service (VPNService): Service for managing VPN subscriptions.
        bot (Bot): The bot instance to send messages and interact with the user.
    """
    logger.info(f"Payment successful for user {message.from_user.id}")
    data = SubscriptionData.unpack(message.successful_payment.invoice_payload)
    logger.debug(f"Subscription data unpacked: {data}")

    if await IsDev()(message):
        await bot.refund_star_payment(
            user_id=message.from_user.id,
            telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id,
        )

    await bot.delete_message(chat_id=message.chat.id, message_id=data.message_id)
    # await bot.edit_message_text(
    #     text="Successful payment!",
    #     chat_id=message.chat.id,
    #     message_id=data.message_id,
    #     reply_markup=back_to_main_menu_keyboard(),
    # )

    if data.is_extend:
        await vpn_service.extend_subscription(data.user_id, data.devices, data.duration)
        logger.info(f"Subscription extented for user {data.user_id}")
    else:
        await vpn_service.create_subscription(data.user_id, data.devices, data.duration)
        logger.info(f"Subscription created for user {data.user_id}")

    await Transaction.create(
        session=session,
        user_id=message.from_user.id,
        plan=message.successful_payment.invoice_payload,
        payment_id=message.successful_payment.telegram_payment_charge_id,
        amount=message.successful_payment.total_amount,
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
        key = await vpn_service.get_key(message.from_user.id)
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
