from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, User

from .is_dev import IsDev


class IsAdmin(BaseFilter):
    """
    Filter to check if the user is an admin.

    Checks if the user who triggered the event is in the list of admin IDs,
    or if the user is the developer. Admin IDs are set using the `set_admins` method.

    Attributes:
        admins_ids (list): List of admin user IDs.
    """

    admins_ids: list[int] = []

    async def __call__(self, event: TelegramObject) -> bool:
        """
        Check if the user is an admin.

        Arguments:
            event (TelegramObject): The event object (e.g., Message).

        Returns:
            bool: True if the user is an admin or the developer, False otherwise.
        """
        user: User | None = getattr(event, "from_user", None)

        if not user:
            return False

        is_dev = await IsDev()(event)
        return user.id in self.admins_ids or is_dev

    @classmethod
    def set_admins(cls, admins_ids: list[int]) -> None:
        """
        Set the list of admin user IDs.

        Arguments:
            admins_ids (list[int]): List of admin IDs.
        """
        IsAdmin.admins_ids = admins_ids
