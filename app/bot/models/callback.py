from aiogram.filters.callback_data import CallbackData

from app.bot.utils.navigation import NavAdminTools, NavSubscription


class SubscriptionData(CallbackData, prefix="subscription"):
    state: NavSubscription
    is_extend: bool = False
    user_id: int = 0
    message_id: int = 0  # need delete
    devices: int = 0
    duration: int = 0
    price: int = 0
