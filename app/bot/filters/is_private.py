from aiogram.enums import ChatType
from aiogram.filters import BaseFilter
from aiogram.types import Chat, TelegramObject


class IsPrivate(BaseFilter):
    """
    Filter for checking if a message is in a private chat.
    """

    async def __call__(self, event: TelegramObject, event_chat: Chat) -> bool:
        """
        Call the filter.

        Arguments:
            event (TelegramObject): The event object (e.g., Message) to check.
            event_chat (Chat): The chat object associated with the event.
        Returns:
            bool: True if the message is in a private chat, False otherwise.
        """
        return event_chat.type == ChatType.PRIVATE
