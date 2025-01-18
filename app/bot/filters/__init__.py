from aiogram import Dispatcher

from .is_admin import IsAdmin
from .is_dev import IsDev
from .is_private import IsPrivate


def register(dispatcher: Dispatcher, developer_id: int, admins_ids: list[int]) -> None:
    """
    Register filters and set developer/admin information.

    Arguments:
        dispatcher (Dispatcher): Dispatcher instance to register filters.
        developer_id (int): The ID of the developer.
        admins_ids (list[int]): List of admin IDs.
    """
    dispatcher.update.filter(IsPrivate())
    IsDev.set_developer(developer_id)
    IsAdmin.set_admins(admins_ids)
