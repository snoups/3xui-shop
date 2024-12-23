from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject


class IsAdmin(BaseFilter):
    """
    Filter for checking if the user is an admin.

    This filter checks whether a user is an administrator based on their user ID.
    The list of admin IDs can be set using the `set_admins` method. When the filter
    is applied, it checks if the user who triggered the event is in the list of administrators.

    Attributes:
        admins (list[int]): List of admin user IDs.
    """

    admins: list[int] = []

    @classmethod
    def set_admins(cls, admins: list[int]) -> None:
        """
        Set the list of admin user IDs.

        This method allows you to update the list of administrators that the filter
        will use to check if a user is an admin.

        Arguments:
            admins (list[int]): List of admin IDs.
        """
        cls.admins = admins

    async def __call__(self, event: TelegramObject) -> bool:
        """
        Call the filter to check if the user is an admin.

        Arguments:
            event (TelegramObject): The event object (e.g., Message) to check.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        if not hasattr(event, "from_user") or not event.from_user:
            return False
        return event.from_user.id in self.admins
