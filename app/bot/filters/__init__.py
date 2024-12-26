from .is_admin import IsAdmin
from .is_maintenance_mode import IsMaintenanceMode
from .is_private import IsPrivate


def register_admins(admins_ids: list[int]) -> None:
    """
    Registers the list of bot administrators.

    This function sets the global list of administrator IDs for the IsAdmin filter.
    By calling this function, you make the provided list of admin IDs available for
    the IsAdmin filter to use when checking if a user is an administrator.

    Arguments:
        admins (list[int]): List of administrator IDs.
    """
    IsAdmin.set_admins(admins_ids)


__all__ = [
    "IsAdmin",
    "IsMaintenanceMode",
    "IsPrivate",
]
