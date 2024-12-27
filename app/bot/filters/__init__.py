from .is_admin import IsAdmin
from .is_dev import IsDev
from .is_private import IsPrivate


def register_admins(admins_ids: list[int]) -> None:
    """
    Register bot administrators.

    Sets the global list of administrator IDs for the IsAdmin filter, enabling it
    to identify administrators during bot interactions.

    Arguments:
        admins_ids (list[int]): List of administrator IDs.
    """
    IsAdmin.set_admins(admins_ids)


def register_developer(developer_id: int) -> None:
    """
    Register the bot developer.

    Sets the developer ID for the IsDev filter, allowing the bot to recognize
    the developer during interactions.

    Arguments:
        developer_id (int): ID of the developer.
    """
    IsDev.set_developer(developer_id)


__all__ = [
    "IsAdmin",
    "IsDev",
    "IsPrivate",
    "register_admins",
    "register_developer",
]
