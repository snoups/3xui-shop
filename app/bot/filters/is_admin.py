from aiogram.filters import BaseFilter
from aiogram.types import Chat, TelegramObject


class IsAdmin(BaseFilter):
    """
    Filter for checking if the user is an admin.
    """

    admins: list[int] = []

    @classmethod
    def set_admins(cls, admins: list[int]) -> None:
        """
        Set the list of admin user IDs.

        Arguments:
            admins (list[int]): List of admin IDs.
        """
        cls.admins = admins

    async def __call__(self, event: TelegramObject) -> bool:
        """
        Call the filter.

        Arguments:
            event (TelegramObject): The event object (e.g., Message) to check.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        if not hasattr(event, "from_user") or not event.from_user:
            return False
        return event.from_user.id in self.admins
