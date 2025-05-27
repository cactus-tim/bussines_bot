"""
DB Operations

CRUD operations for users, club_events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (select)

from database.models import (
    Questionary,
    async_session, )
from errors.errors import (
    Error404,
    Error409,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------
@db_error_handler
async def get_questionary(tg_id: int):
    """
    Retrieve a questionary by user ID.

    Args:
        tg_id (int): Telegram user identifier.

    Returns:
        Questionary or str: Questionary object or "not created".
    """
    async with async_session() as session:
        q = await session.scalar(
            select(Questionary).where(Questionary.user_id == tg_id)
        )
        if q:
            return q
        return "not created"


# --------------------------------------------------------------------------------
@db_error_handler
async def create_questionary(tg_id: int):
    """
    Create a new questionary for a user.

    Args:
        tg_id (int): Telegram user identifier.

    Returns:
        None
    """
    async with async_session() as session:
        q = await get_questionary(tg_id)
        if q == "not created":
            session.add(Questionary(user_id=tg_id))
            await session.commit()
        else:
            raise Error409


# --------------------------------------------------------------------------------
@db_error_handler
async def update_questionary(tg_id: int, data: dict):
    """
    Update existing questionary data.

    Args:
        tg_id (int): Telegram user identifier.
        data (dict): Fields to update with values.

    Returns:
        None
    """
    async with async_session() as session:
        q = await get_questionary(tg_id)
        if q == "not created":
            raise Error404
        for key, value in data.items():
            setattr(q, key, value)
        session.add(q)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_quests():
    """
    Fetch all questionaries.

    Returns:
        list[Questionary]: List of Questionary objects.
    """
    async with async_session() as session:
        result = await session.execute(select(Questionary))
        quests = result.scalars().all()
        if not quests:
            raise Error404
        return quests
