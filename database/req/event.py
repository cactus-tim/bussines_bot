"""
DB Operations

CRUD operations for users, events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (distinct, select)

from database.models import (
    Event,
    async_session, )
from errors.errors import (
    Error404,
    EventNameError,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------
@db_error_handler
async def get_event(name: str):
    """
    Retrieve an event by name.

    Args:
        name (str): Event name.

    Returns:
        Event or str: Event object or "not created".
    """
    async with async_session() as session:
        evt = await session.scalar(
            select(Event).where(Event.name == name)
        )
        if evt:
            return evt
        return "not created"


# --------------------------------------------------------------------------------
@db_error_handler
async def create_event(name: str, data: dict):
    """
    Create a new event.

    Args:
        name (str): Event name.
        data (dict): Event data fields.

    Returns:
        str: Confirmation message.
    """
    async with async_session() as session:
        evt = await get_event(name)
        if evt == "not created":
            data["name"] = name
            data["status"] = "in_progress"
            session.add(Event(**data))
            await session.commit()
            return "all ok"
        raise EventNameError


# --------------------------------------------------------------------------------
@db_error_handler
async def update_event(name: str, data: dict):
    """
    Update existing event data.

    Args:
        name (str): Event name.
        data (dict): Fields to update.

    Returns:
        None
    """
    async with async_session() as session:
        evt = await get_event(name)
        if evt == "not created":
            raise Error404
        for key, value in data.items():
            setattr(evt, key, value)
        session.add(evt)
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_events_in_p():
    """
    Fetch names of events in progress.

    Returns:
        list[str]: List of event names.
    """
    async with async_session() as session:
        result = await session.execute(
            select(distinct(Event.name)).where(
                Event.status == "in_progress"
            )
        )
        names = result.scalars().all()
        if not names:
            raise Error404
        return names


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_events():
    """
    Fetch all event names.

    Returns:
        list[str]: List of event names.
    """
    async with async_session() as session:
        result = await session.execute(
            select(distinct(Event.name))
        )
        names = result.scalars().all()
        if not names:
            raise Error404
        return names
