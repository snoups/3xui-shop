from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, User


class IsDev(BaseFilter):
    """
    Filter to check if the user is the developer.

    This filter checks if the user who triggered the event is the developer
    by comparing their ID to the registered developer ID.

    Attributes:
        developer_id (int): The ID of the bot developer.
    """

    developer_id: int

    async def __call__(self, event: TelegramObject) -> bool:
        """
        Check if the user is the developer.

        Arguments:
            event (TelegramObject): The event object (e.g., Message) to check.

        Returns:
            bool: True if the user is the developer, False otherwise.
        """
        user: User | None = getattr(event, "from_user", None)

        if not user:
            return False

        return user.id == self.developer_id

    @classmethod
    def set_developer(cls, developer_id: int) -> None:
        """
        Set the developer ID.

        Arguments:
            developer_id (int): The ID of the developer.
        """
        cls.developer_id = developer_id
