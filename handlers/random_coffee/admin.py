"""
Random Coffee Stats

Handlers for displaying overall and weekly Random Coffee statistics.
"""

# --------------------------------------------------------------------------------

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import (
    RandomCoffeeProfile,
    RandomCoffeeWeek,
    RandomCoffeePair,
    RandomCoffeeFeedback,
    User
)
from utils.random_coffee.helpers import get_week_start_date

# --------------------------------------------------------------------------------

router = Router()

# --------------------------------------------------------------------------------

@router.message(Command("coffee_stats"))
async def cmd_coffee_stats(message: Message, session: AsyncSession):
    """
    Display overall Random Coffee statistics for superusers.

    Args:
        message (Message): Incoming message from a Telegram user.
        session (AsyncSession): SQLAlchemy async session for DB operations.

    Returns:
        None
    """
    user = await session.get(User, message.from_user.id)
    if not user or not user.is_superuser:
        return

    current_week = get_week_start_date()

    total_profiles = await session.scalar(
        select(func.count()).select_from(RandomCoffeeProfile)
    )

    current_participants = await session.scalar(
        select(func.count()).select_from(RandomCoffeeWeek).where(
            RandomCoffeeWeek.week_start == current_week.isoformat(),
            RandomCoffeeWeek.is_participating.is_(True)
        )
    )

    total_pairs = await session.scalar(
        select(func.count()).select_from(RandomCoffeePair)
    )

    feedback_count = await session.scalar(
        select(func.count()).select_from(RandomCoffeeFeedback)
    )

    avg_rating = await session.scalar(
        select(func.avg(RandomCoffeeFeedback.rating))
    )

    avg_rating_str = f"{avg_rating:.1f}" if avg_rating is not None else "Нет данных"

    stats_message = (
        "📊 Статистика Random Coffee:\n\n"
        f"👥 Всего профилей: {total_profiles}\n"
        f"✅ Участников на этой неделе: {current_participants}\n"
        f"🤝 Всего создано пар: {total_pairs}\n"
        f"⭐️ Средняя оценка встреч: {avg_rating_str}\n"
        f"📝 Всего отзывов: {feedback_count}\n"
    )

    await message.answer(stats_message)

# --------------------------------------------------------------------------------

@router.message(Command("coffee_week_stats"))
async def cmd_coffee_week_stats(message: Message, session: AsyncSession):
    """
    Display current week's Random Coffee statistics for superusers.

    Args:
        message (Message): Incoming message from a Telegram user.
        session (AsyncSession): SQLAlchemy async session for DB operations.

    Returns:
        None
    """
    user = await session.get(User, message.from_user.id)
    if not user or not user.is_superuser:
        return

    current_week = get_week_start_date()

    participant_rows = await session.scalars(
        select(RandomCoffeeWeek).where(
            RandomCoffeeWeek.week_start == current_week.isoformat(),
            RandomCoffeeWeek.is_participating.is_(True)
        )
    )
    participant_ids = {p.user_id for p in participant_rows}

    stats_message = (
        f"📅 Статистика за неделю {current_week.strftime('%d.%m.%Y')}:\n\n"
        f"👥 Участников: {len(participant_ids)}"
    )

    await message.answer(stats_message)
