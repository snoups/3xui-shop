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

from app.bot.routers.misc.keyboard import close_notification_keyboard
from app.config import Config

logger = logging.getLogger(__name__)


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
        reply_markup: (
            InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None
        ) = None,
        document: InputFile | None = None,
        bot: Bot | None = None,
    ) -> Message | None:
        logger.debug(f"Sending notification for {chat_id}")

        if not (message or chat_id):
            logger.error("Failed to send notification: message or chat_id required")
            return None

        if message and not bot:
            bot = message.bot

        chat_id = message.chat.id if message else chat_id

        if duration == 0 and reply_markup is None:
            reply_markup = close_notification_keyboard()

        try:
            if document:
                send_method = bot.send_document if bot else message.answer_document
                args = {"document": document, "caption": text}
            else:
                send_method = bot.send_message if bot else message.answer
                args = {"text": text}

            notification = await send_method(
                chat_id=chat_id,
                reply_markup=reply_markup,
                **args,
            )
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
        reply_markup: (
            InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None
        ) = None,
        document: InputFile | None = None,
    ) -> None:
        await self._notify(
            text=text,
            duration=duration,
            chat_id=chat_id,
            reply_markup=reply_markup,
            document=document,
            bot=self.bot,
        )

    @staticmethod
    async def notify_by_message(
        message: Message,
        text: str,
        duration: int = 0,
        reply_markup: (
            InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None
        ) = None,
        document: InputFile | None = None,
    ) -> None:
        await NotificationService._notify(
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
        reply_markup: (
            InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None
        ) = None,
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
        reply_markup: (
            InlineKeyboardMarkup | ReplyKeyboardMarkup | ReplyKeyboardRemove | ForceReply | None
        ) = None,
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
