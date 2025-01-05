import asyncio
import logging

from aiogram import Bot
from aiogram.types import Message

from app.bot.keyboards.notification import close_notification_keyboard

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service to send notifications to users in Telegram with optional removal after a delay.

    Attributes:
        bot (Bot): The aiogram Bot instance used to send messages.
    """

    def __init__(self, bot: Bot) -> None:
        """
        Initializes the NotificationService with a Bot instance.

        Arguments:
            bot (Bot): The aiogram Bot instance used to send messages.
        """
        self.bot = bot
        logger.info("NotificationService initialized.")

    async def notify_by_id(self, chat_id: int, text: str, duration: int = 0) -> None:
        """
        Sends a notification message to the user with the specified chat ID.

        If a duration is provided, the message will be deleted after the specified time.

        Arguments:
            chat_id (int): The ID of the chat to send the notification to.
            text (str): The content of the notification message.
            duration (int): The duration (in seconds) to keep the message before deleting.
                            Defaults to 0 (doesn't delete the message).
        """
        logger.info(f"Sending notification for {chat_id}.")
        notification: Message

        if duration > 0:
            notification = await self.bot.send_message(chat_id=chat_id, text=text)
            logger.debug(f"Notification sent. Waiting for {duration} seconds before deletion.")
            await asyncio.sleep(duration)
            await notification.delete()
            logger.debug(f"Notification deleted after {duration} seconds.")
            return
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=close_notification_keyboard(),
            )

    @staticmethod
    async def notify_by_message(message: Message, text: str, duration: int = 0) -> None:
        """
        Sends a notification message in reply to the specified message.

        If a duration is provided, the message will be deleted after the specified time.

        Arguments:
            message (Message): The Message object to reply to.
            text (str): The content of the notification message.
            duration (int): The duration (in seconds) to keep the message before deleting.
                            Defaults to 0 (doesn't delete the message).
        """
        logger.info(f"Sending notification for {message.chat.id}.")
        notification: Message

        if duration > 0:
            notification = await message.answer(text=text)
            logger.debug(f"Notification sent. Waiting for {duration} seconds before deletion.")
            await asyncio.sleep(duration)
            await notification.delete()
            logger.debug(f"Notification deleted after {duration} seconds.")
            return
        else:
            await message.answer(text=text, reply_markup=close_notification_keyboard())
