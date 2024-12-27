from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject


class IsDev(BaseFilter):
    """
    Filter to check if a user is an admin.

    This filter checks if the user who triggered the event is in the list of admin IDs.
    The list of admin IDs can be set using the `set_admins` method.

    Attributes:
        admins_ids (list[int]): List of admin user IDs.
    """

    developer_id: int

    @classmethod
    def set_developer(cls, developer_id: int) -> None:
        """
        Set the list of admin user IDs.

        Arguments:
            admins_ids (list[int]): List of admin IDs.
        """
        cls.developer_id = developer_id

    async def __call__(self, event: TelegramObject) -> bool:
        """
        Check if the user is an admin.

        Arguments:
            event (TelegramObject): The event object (e.g., Message) to check.

        Returns:
            bool: True if the user is an admin, False otherwise.
        """
        if not hasattr(event, "from_user") or not event.from_user:
            return False
        return event.from_user.id == self.developer_id
