import asyncio
import logging

from aiogram import Bot
from aiogram.types import (
    CallbackQuery,
    ForceReply,
    InlineKeyboardMarkup,
    InputFile,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __

from app.bot.models.subscription_data import SubscriptionData
from app.bot.routers.misc.keyboard import close_notification_keyboard
from app.bot.routers.subscription.keyboard import payment_success_keyboard
from app.bot.utils.constants import MESSAGE_EFFECT_IDS
from app.bot.utils.formatting import format_device_count, format_subscription_period
from app.config import Config

logger = logging.getLogger(__name__)

ReplyMarkupType = (
    InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None
)


class NotificationService:
    def __init__(self, config: Config, bot: Bot) -> None:
        self.config = config
        self.bot = bot
        logger.info("Notification Service initialized.")

    @staticmethod
    async def _notify(
        text: str,
        duration: int,
        *,
        message: Message | None = None,
        chat_id: int | None = None,
        reply_markup: ReplyMarkupType = None,
        document: InputFile | None = None,
        bot: Bot | None = None,
        message_effect_id: str | None = None,
    ) -> Message | None:
        if not (message or chat_id):
            logger.error("Failed to send notification: message or chat_id required")
            return None

        if message and not bot:
            bot = message.bot

        chat_id = message.chat.id if message else chat_id

        if duration == 0 and reply_markup is None:
            reply_markup = close_notification_keyboard()

        send_method = bot.send_document if document else bot.send_message
        args = {"document": document, "caption": text} if document else {"text": text}

        if message_effect_id:
            args["message_effect_id"] = message_effect_id

        try:
            notification = await send_method(chat_id=chat_id, reply_markup=reply_markup, **args)
            logger.debug(f"Notification sent to {chat_id}")
        except Exception as exception:
            logger.error(f"Failed to send notification: {exception}")
            return None

        if duration > 0:
            await asyncio.sleep(duration)
            try:
                await notification.delete()
            except Exception as exception:
                logger.error(f"Failed to delete message {notification.message_id}: {exception}")

        return notification

    async def notify_by_id(
        self,
        chat_id: int,
        text: str,
        duration: int = 0,
        reply_markup: ReplyMarkupType = None,
        document: InputFile | None = None,
        message_effect_id: str | None = None,
    ) -> Message | None:
        return await self._notify(
            text=text,
            duration=duration,
            chat_id=chat_id,
            reply_markup=reply_markup,
            document=document,
            bot=self.bot,
            message_effect_id=message_effect_id,
        )

    @staticmethod
    async def notify_by_message(
        message: Message,
        text: str,
        duration: int = 0,
        reply_markup: ReplyMarkupType = None,
        document: InputFile | None = None,
    ) -> Message | None:
        return await NotificationService._notify(
            text=text,
            duration=duration,
            message=message,
            reply_markup=reply_markup,
            document=document,
        )

    async def notify_admins(
        self,
        text: str,
        duration: int = 0,
        reply_markup: ReplyMarkupType = None,
        document: InputFile | None = None,
    ) -> None:
        if not self.config.bot.ADMINS:
            logger.warning("Admin list is empty. No notifications will be sent.")
            return

        for chat_id in self.config.bot.ADMINS:
            await self._notify(
                text=text,
                duration=duration,
                chat_id=chat_id,
                reply_markup=reply_markup,
                document=document,
                bot=self.bot,
            )

    async def notify_developer(
        self,
        text: str,
        duration: int = 0,
        reply_markup: ReplyMarkupType = None,
        document: InputFile | None = None,
    ) -> None:
        await self._notify(
            text=text,
            duration=duration,
            chat_id=self.config.bot.DEV_ID,
            reply_markup=reply_markup,
            document=document,
            bot=self.bot,
        )

    @staticmethod
    async def show_popup(callback: CallbackQuery, text: str, cache_time: int = 0) -> None:
        try:
            await callback.answer(text=text, show_alert=True, cache_time=cache_time)
            logger.debug(f"Popup sent to {callback.from_user.id}")
        except Exception as exception:
            logger.error(f"Failed to send popup: {exception}")

    async def notify_purchase_success(
        self,
        user_id: int,
        key: str,
        message_effect_id: str = MESSAGE_EFFECT_IDS["🎉"],
    ) -> None:
        await self.notify_by_id(
            chat_id=user_id,
            text=__("payment:message:purchase_success").format(key=key),
            message_effect_id=message_effect_id,
            reply_markup=payment_success_keyboard(),
        )

    async def notify_extend_success(
        self,
        user_id: int,
        data: SubscriptionData,
        message_effect_id: str = MESSAGE_EFFECT_IDS["🎉"],
    ) -> None:
        await self.notify_by_id(
            chat_id=user_id,
            text=__("payment:message:extend_success").format(
                duration=format_subscription_period(data.duration)
            ),
            message_effect_id=message_effect_id,
        )

    async def notify_change_success(
        self,
        user_id: int,
        data: SubscriptionData,
        message_effect_id: str = MESSAGE_EFFECT_IDS["🎉"],
    ) -> None:
        await self.notify_by_id(
            chat_id=user_id,
            text=__("payment:message:change_success").format(
                device=format_device_count(data.devices),
                duration=format_subscription_period(data.duration),
            ),
            message_effect_id=message_effect_id,
        )
