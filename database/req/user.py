"""
DB Operations

CRUD operations for users, club_events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (distinct, func, select, over)

from database.models import (
    User,
    async_session, )
from errors.errors import (
    Error404,
    Error409,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------
@db_error_handler
async def get_user(tg_id: int):
    """
    Retrieve a user by Telegram ID.

    Args:
        tg_id (int): Telegram user identifier.

    Returns:
        User or str: User object or "not created".
    """
    async with async_session() as session:
        user = await session.scalar(
            select(User).where(User.id == tg_id)
        )
        if user:
            return user
        return "not created"


# --------------------------------------------------------------------------------
@db_error_handler
async def create_user(tg_id: int, data: dict):
    """
    Create a new user.

    Args:
        tg_id (int): Telegram user identifier.
        data (dict): User data fields.

    Returns:
        User: Newly created User object.
    """
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == "not created":
            data["id"] = tg_id
            new_user = User(**data)
            session.add(new_user)
            await session.commit()
            return new_user
        raise Error409


# --------------------------------------------------------------------------------
@db_error_handler
async def update_user(tg_id: int, data: dict):
    """
    Update existing user data.

    Args:
        tg_id (int): Telegram user identifier.
        data (dict): Fields to update with values.

    Returns:
        None
    """
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == "not created":
            raise Error404
        for key, value in data.items():
            setattr(user, key, value)
        session.add(user)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def get_users_tg_id():
    """
    Fetch all distinct Telegram IDs of users.

    Returns:
        list[int]: List of user Telegram IDs.
    """
    async with async_session() as session:
        result = await session.execute(
            select(distinct(User.id))
        )
        ids = result.scalars().all()
        if not ids:
            raise Error404
        return ids


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_users():
    """
    Fetch all user records.

    Returns:
        list[User]: List of User objects.
    """
    async with async_session() as session:
        result = await session.execute(select(User))
        users = result.scalars().all()
        if not users:
            raise Error404
        return users


# --------------------------------------------------------------------------------
@db_error_handler
async def add_money(tg_id: int, cnt: int):
    """
    Increment user's money balance.

    Args:
        tg_id (int): Telegram user ID.
        cnt (int): Amount to add.

    Raises:
        Error404: If user not created.
    """
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        setattr(user, 'money', user.money + cnt)
        session.add(user)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def one_more_event(tg_id: int):
    """
    Increment user's event count by one.

    Args:
        tg_id (int): Telegram user ID.

    Raises:
        Error404: If user not created.
    """
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        setattr(user, 'event_cnt', user.event_cnt + 1)
        session.add(user)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def add_referal_cnt(tg_id: int):
    """
    Increment user's referral count by one.

    Args:
        tg_id (int): Telegram user ID.

    Raises:
        Error404: If user not created.
    """
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        setattr(user, 'ref_cnt', user.ref_cnt + 1)
        session.add(user)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def update_strick(tg_id: int, cnt: int = 1):
    """
    Update user's strike count.

    Args:
        tg_id (int): Telegram user ID.
        cnt (int): Strike increment or reset flag.

    Raises:
        Error404: If user not created.
    """
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        if cnt == 0:
            setattr(user, 'strick', 0)
        else:
            setattr(user, 'strick', user.strick + 1)
        session.add(user)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def get_user_rank_by_money(specific_user_id: int) -> int:
    """
    Get ranking of a user by money.

    Args:
        specific_user_id (int): User identifier.

    Returns:
        int: User rank by descending money.

    Raises:
        Error404: If user not found in ranking.
    """
    async with async_session() as session:
        rank_column = over(
            func.row_number(), order_by=User.money.desc()
        ).label('rank')
        subquery = (
            select(User.id, rank_column)
            .subquery()
        )
        query = select(subquery.c.rank).where(
            subquery.c.id == specific_user_id
        )
        result = await session.execute(query)
        user_rank = result.scalar()
        if user_rank is None:
            raise Error404
        return user_rank


# --------------------------------------------------------------------------------
@db_error_handler
async def get_top_10_users_by_money() -> list[User]:
    """
    Retrieve top ten users by money.

    Returns:
        list[User]: List of top users.
    """
    async with async_session() as session:
        query = (
            select(User)
            .order_by(User.money.desc())
            .limit(10)
        )
        result = await session.execute(query)
        top_users = result.scalars().all()
        return top_users
