"""
DB Operations

CRUD operations for users, club_events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------

from sqlalchemy import select

from database.models import RegEvent, async_session
from errors.errors import Error404, Error409
from errors.handlers import db_error_handler

# --------------------------------------------------------------------------------

@db_error_handler
async def get_reg_event(tg_id: int):
    """
    Retrieve registration event data by Telegram ID.

    Args:
        tg_id (int): Telegram user ID for registration.

    Returns:
        RegEvent: Registration event data.
    """
    async with async_session() as session:
        reg_event = await session.scalar(
            select(RegEvent).where(RegEvent.id == tg_id)
        )
        if reg_event:
            return reg_event
        else:
            raise Error404

# --------------------------------------------------------------------------------

@db_error_handler
async def create_reg_event(tg_id: int):
    """
    Create a new registration event entry.

    Args:
        tg_id (int): Telegram user ID for registration.

    Returns:
        None
    """
    async with async_session() as session:
        reg_event = await get_reg_event(tg_id)
        if not reg_event:
            data = {'id': tg_id}
            reg_event_data = RegEvent(**data)
            session.add(reg_event_data)
            await session.commit()
        else:
            raise Error409

# --------------------------------------------------------------------------------

@db_error_handler
async def update_reg_event(tg_id: int, data: dict):
    """
    Update fields of an existing registration event.

    Args:
        tg_id (int): Telegram user ID for registration.
        data (dict): Fields to update with values.

    Returns:
        None
    """
    async with async_session() as session:
        reg_event = await get_reg_event(tg_id)
        if not reg_event:
            raise Error404
        for key, value in data.items():
            setattr(reg_event, key, value)
        session.add(reg_event)
        await session.commit()

# --------------------------------------------------------------------------------

@db_error_handler
async def check_completly_reg_event(tg_id: int):
    """
    Check if all registration fields are filled.

    Args:
        tg_id (int): Telegram user ID for registration.

    Returns:
        bool: True if all fields non-empty, False otherwise.
    """
    async with async_session() as session:
        reg_event = await get_reg_event(tg_id)
        if not reg_event:
            return False
        if (
            reg_event.name == '' or
            reg_event.surname == '' or
            reg_event.fathername == '' or
            reg_event.mail == '' or
            reg_event.phone == '' or
            reg_event.org == ''
        ):
            return False
        return True
