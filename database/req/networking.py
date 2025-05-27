"""
DB Operations

CRUD operations for users, club_events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (delete, select)

from database.models import (
    Networking,
    async_session, )
from errors.errors import (
    Error404,
    Error409,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------
@db_error_handler
async def add_user_to_networking(tg_id: int):
    """
    Add a user to networking table.

    Args:
        tg_id (int): Telegram user ID.

    Returns:
        str: Confirmation message 'ok'.

    Raises:
        Error409: If user already in networking.
    """
    async with async_session() as session:
        existing_user = await session.scalar(
            select(Networking.id).where(Networking.id == tg_id)
        )
        if existing_user:
            raise Error409
        networking = Networking(id=tg_id)
        session.add(networking)
        await session.commit()
        return 'ok'


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_for_networking():
    """
    Retrieve all user IDs from networking.

    Returns:
        list[int]: List of networking user IDs.

    Raises:
        Error404: If no networking data.
    """
    async with async_session() as session:
        networking = await session.execute(select(Networking.id))
        networking_data = networking.scalars().all()
        if not networking_data:
            raise Error404
        return networking_data


# --------------------------------------------------------------------------------
@db_error_handler
async def delete_all_from_networking():
    """
    Delete all entries from networking table.
    """
    async with async_session() as session:
        await session.execute(delete(Networking))
        await session.commit()
