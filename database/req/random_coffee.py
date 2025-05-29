"""
Random Coffee Helpers

Utility functions for profile handling, pairing, formatting and validation.
"""

# --------------------------------------------------------------------------------

from datetime import datetime
from typing import List, Tuple, Optional

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RandomCoffeeProfile, RandomCoffeeWeek, RandomCoffeePair, User


# --------------------------------------------------------------------------------

async def get_user_profile(session: AsyncSession, user_id: int) -> Optional[RandomCoffeeProfile]:
    """
    Get user's Random Coffee profile.

    Args:
        session (AsyncSession): Database session.
        user_id (int): Telegram user ID.

    Returns:
        Optional[RandomCoffeeProfile]: User profile or None.
    """
    query = select(RandomCoffeeProfile).where(RandomCoffeeProfile.user_id == user_id)
    result = await session.execute(query)
    return result.scalar_one_or_none()


# --------------------------------------------------------------------------------

async def get_participating_users(session: AsyncSession, week_start: datetime) -> List[User]:
    """
    Get list of users participating in Random Coffee for the given week.

    Args:
        session (AsyncSession): Database session.
        week_start (datetime): Week identifier.

    Returns:
        List[User]: Participating users.
    """
    query = select(User).join(
        RandomCoffeeWeek,
        and_(
            User.id == RandomCoffeeWeek.user_id,
            RandomCoffeeWeek.week_start == week_start.isoformat(),
            RandomCoffeeWeek.is_participating == True
        )
    )
    result = await session.execute(query)
    return result.scalars().all()


# --------------------------------------------------------------------------------

async def save_pairs(session: AsyncSession, pairs: List[Tuple[User, User]], week_start: datetime):
    """
    Save user pairs to the database.

    Args:
        session (AsyncSession): Database session.
        pairs (List[Tuple[User, User]]): List of user pairs.
        week_start (datetime): Week identifier.

    Returns:
        None
    """
    for user1, user2 in pairs:
        pair = RandomCoffeePair(
            week_start=week_start.isoformat(),
            user1_id=user1.id,
            user2_id=user2.id,
            created_at=datetime.now().isoformat()
        )
        session.add(pair)
    await session.commit()
