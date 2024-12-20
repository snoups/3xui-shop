from aiogram import Dispatcher

from app.bot.filters.is_admin import IsAdmin

from .is_private import IsPrivate


def register_admins(admins: list[int]) -> None:
    """
    Registers the list of bot administrators.

    This function sets the global list of administrator IDs for the IsAdmin filter.

    Arguments:
        admins (list[int]): List of administrator IDs.
    """
    IsAdmin.admins = admins


__all__ = [
    "IsAdmin",
    "IsPrivate",
]
