"""
Random Coffee Helpers

Utility functions for profile handling, pairing, formatting and validation.
"""

# --------------------------------------------------------------------------------

import random
import re
from datetime import datetime, timedelta
from typing import List, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RandomCoffeeProfile, User


# --------------------------------------------------------------------------------

def validate_birth_date(date_str: str) -> bool:
    """
    Validate birth date format (DD.MM.YYYY).

    Args:
        date_str (str): Birth date string.

    Returns:
        bool: True if valid format and real date, else False.
    """
    pattern = r'^\d{2}\.\d{2}\.\d{4}$'
    if not re.match(pattern, date_str):
        return False
    try:
        day, month, year = map(int, date_str.split('.'))
        datetime(year, month, day)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------------

def get_week_start_date(date: datetime = None) -> datetime:
    """
    Get the datetime of Monday this week at 23:59:59.999999.

    Args:
        date (datetime, optional): Reference date.

    Returns:
        datetime: The Monday of the same week at end of day.
    """
    if date is None:
        date = datetime.now()
    monday = date - timedelta(days=date.weekday())
    monday_end = monday.replace(hour=23, minute=59, second=59, microsecond=999999)
    return monday_end


# --------------------------------------------------------------------------------

def profile_similarity(p1: RandomCoffeeProfile, p2: RandomCoffeeProfile) -> int:
    """
    Evaluate similarity score between two profiles.

    Args:
        p1 (RandomCoffeeProfile): First profile.
        p2 (RandomCoffeeProfile): Second profile.

    Returns:
        int: Similarity score (higher is better).
    """
    score = 0

    if p1.city == p2.city:
        score += 3
    if p1.meeting_format == p2.meeting_format:
        score += 2
    if p1.meeting_goal == p2.meeting_goal:
        score += 2

    hobbies1 = set(p1.hobbies.lower().split())
    hobbies2 = set(p2.hobbies.lower().split())
    common_hobbies = hobbies1.intersection(hobbies2)
    score += len(common_hobbies)

    return score


# --------------------------------------------------------------------------------

async def create_smart_pairs(session: AsyncSession, users: List[User]) -> List[Tuple[User, User]]:
    """
    Create user pairs based on profile similarity.

    Args:
        session (AsyncSession): Database session.
        users (List[User]): List of users.

    Returns:
        List[Tuple[User, User]]: List of matched pairs.
    """
    profiles = await session.execute(
        select(RandomCoffeeProfile).where(
            RandomCoffeeProfile.user_id.in_([u.id for u in users])
        )
    )
    profile_map = {p.user_id: p for p in profiles.scalars().all()}
    user_pool = users[:]
    random.shuffle(user_pool)

    pairs = []

    while len(user_pool) > 1:
        user = user_pool.pop(0)
        best_match = None
        best_score = -1

        for candidate in user_pool:
            score = profile_similarity(profile_map[user.id], profile_map[candidate.id])
            if score > best_score:
                best_match = candidate
                best_score = score

        if best_match:
            user_pool.remove(best_match)
            pairs.append((user, best_match))

    return pairs


# --------------------------------------------------------------------------------

def format_pair_message(user1: User, user2: User) -> str:
    """
    Format message for a pair of users.

    Args:
        user1 (User): First user.
        user2 (User): Second user.

    Returns:
        str: Pair formatted message.
    """
    return f"➪ @{user1.handler} x @{user2.handler}"


# --------------------------------------------------------------------------------

def format_pairs_message(pairs: List[Tuple[User, User]], chat_title: str) -> str:
    """
    Format full message for all pairs.

    Args:
        pairs (List[Tuple[User, User]]): List of user pairs.
        chat_title (str): Title of the group chat.

    Returns:
        str: Full formatted announcement.
    """
    message = f"Пары для {chat_title} составлены!\n"
    message += "Ищи в списке ниже, с кем встречаешься на этой неделе:\n\n"
    for user1, user2 in pairs:
        message += format_pair_message(user1, user2) + "\n"
    message += "\nНапиши собеседнику в личку, чтобы договориться о времени и формате встречи ☕"
    return message


# --------------------------------------------------------------------------------

def get_profile_text(profile: RandomCoffeeProfile) -> str:
    """
    Generate display text for a user's profile.

    Args:
        profile (RandomCoffeeProfile): User profile.

    Returns:
        str: Formatted profile text.
    """
    return (
        f"{profile.full_name} ({profile.city})\n"
        f"<b>Профиль:</b> {profile.social_links}\n\n"
        f"<b>Чем занимается:</b> {profile.occupation}\n"
        f"<b>Зацепки для начала разговора:</b> {profile.hobbies}\n"
        f"<b>От встречи ожидает:</b> {profile.meeting_goal}\n"
    )


# --------------------------------------------------------------------------------

def get_day(day: str) -> str:
    """
    Convert Russian day name to short English code.

    Args:
        day (str): Russian day name.

    Returns:
        str: English day abbreviation or original input.
    """
    day_map = {
        "понедельник": "mon",
        "вторник": "tue",
        "среда": "wed",
        "четверг": "thu",
        "пятница": "fri",
        "суббота": "sat",
        "воскресенье": "sun"
    }
    return day_map.get(day, day)
