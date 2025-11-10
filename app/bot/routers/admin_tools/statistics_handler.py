import logging
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.i18n import gettext as _
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.filters import IsAdmin
from app.bot.utils.navigation import NavAdminTools
from app.db.models import Transaction, User, Server, Promocode, Referral

logger = logging.getLogger(__name__)
router = Router(name=__name__)


async def get_statistics(session: AsyncSession) -> dict:
    """
    Собирает статистику из базы данных.
    
    Args:
        session: Сессия базы данных
        
    Returns:
        Словарь со статистическими данными
    """
    # Получаем общее количество пользователей
    total_users_query = await session.execute(select(func.count()).select_from(User))
    total_users = total_users_query.scalar() or 0

    # Новые пользователи за последние 24 часа
    day_ago = datetime.now() - timedelta(days=1)
    new_users_query = await session.execute(
        select(func.count()).select_from(User).where(User.created_at >= day_ago)
    )
    new_users_24h = new_users_query.scalar() or 0

    # Новые пользователи за последние 7 дней
    week_ago = datetime.now() - timedelta(days=7)
    new_users_week_query = await session.execute(
        select(func.count()).select_from(User).where(User.created_at >= week_ago)
    )
    new_users_7d = new_users_week_query.scalar() or 0

    # Количество активных серверов
    servers_query = await session.execute(select(func.count()).select_from(Server))
    total_servers = servers_query.scalar() or 0

    # Количество транзакций
    transactions_query = await session.execute(select(func.count()).select_from(Transaction))
    total_transactions = transactions_query.scalar() or 0

    # Количество использованных промокодов
    promocodes_query = await session.execute(
        select(func.count()).select_from(Promocode).where(Promocode.is_activated == True)
    )
    used_promocodes = promocodes_query.scalar() or 0

    # Количество рефералов
    referrals_query = await session.execute(select(func.count()).select_from(Referral))
    total_referrals = referrals_query.scalar() or 0

    # Количество пользователей, использовавших пробный период
    trial_users_query = await session.execute(
        select(func.count()).select_from(User).where(User.is_trial_used == True)
    )
    trial_users = trial_users_query.scalar() or 0

    return {
        "total_users": total_users,
        "new_users_24h": new_users_24h,
        "new_users_7d": new_users_7d,
        "total_servers": total_servers,
        "total_transactions": total_transactions,
        "used_promocodes": used_promocodes,
        "total_referrals": total_referrals,
        "trial_users": trial_users
    }


@router.callback_query(F.data == NavAdminTools.STATISTICS, IsAdmin())
async def callback_statistics(callback: CallbackQuery, user: User, session: AsyncSession) -> None:
    """
    Обработчик для отображения статистики администратору.

    Args:
        callback: Объект обратного вызова
        user: Объект пользователя
        session: Сессия базы данных
    """
    logger.info(f"Admin {user.tg_id} opened statistics.")

    # Получаем статистику
    stats = await get_statistics(session)

    # Формируем сообщение со статистикой
    message_text = _(
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 <b>Пользователи:</b>\n"
        f"• Всего: {stats['total_users']}\n"
        f"• Новых за 24ч: {stats['new_users_24h']}\n"
        f"• Новых за 7 дней: {stats['new_users_7d']}\n"
        f"• Использовали пробный период: {stats['trial_users']}\n\n"
        f"🖥 <b>Серверы:</b>\n"
        f"• Всего: {stats['total_servers']}\n\n"
        f"💰 <b>Транзакции:</b>\n"
        f"• Количество: {stats['total_transactions']}\n\n"
        f"🎁 <b>Промокоды:</b>\n"
        f"• Использовано: {stats['used_promocodes']}\n\n"
        f"👋 <b>Рефералы:</b>\n"
        f"• Всего: {stats['total_referrals']}"
    )

    # Создаем клавиатуру для возврата в меню админа
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=_("↩️ Назад"),
                    callback_data=NavAdminTools.MAIN
                )
            ]
        ]
    )

    # Отправляем сообщение со статистикой
    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    await callback.answer()