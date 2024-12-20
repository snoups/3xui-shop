from aiogram.filters import BaseFilter
from aiogram.types import Chat, TelegramObject


class IsAdmin(BaseFilter):
    """
    Filter for checking if the user is an admin.
    """

    admins: list[int] = []

    async def __call__(self, event: TelegramObject, event_chat: Chat) -> bool:
        """
        Call the filter.

        Arguments:
            event (TelegramObject): The event object (e.g., Message) to check.
            event_chat (Chat): The chat object associated with the event.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        user_id = event.from_user.id
        return user_id in self.admins
