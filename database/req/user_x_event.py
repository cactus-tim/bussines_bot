"""
DB Operations

CRUD operations for users, events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (distinct, delete, func, select, and_)

from database.models import (
    Event,
    User,
    UserXEvent,
    async_session, )
from errors.errors import (
    Error404,
    Error409,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------
@db_error_handler
async def get_user_x_event_row(user_id: int, event_name: str):
    """
    Retrieve a UserXEvent row.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.

    Returns:
        UserXEvent or str: Row object or "not created".
    """
    async with async_session() as session:
        row = await session.scalar(
            select(UserXEvent).where(
                and_(
                    UserXEvent.user_id == user_id,
                    UserXEvent.event_name == event_name,
                )
            )
        )
        if row:
            return row
        return "not created"


# --------------------------------------------------------------------------------
@db_error_handler
async def delete_user_x_event_row(user_id: int, event_name: str):
    """
    Delete a UserXEvent row.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.

    Returns:
        None
    """
    async with async_session() as session:
        await session.execute(
            delete(UserXEvent).where(
                and_(
                    UserXEvent.user_id == user_id,
                    UserXEvent.event_name == event_name,
                )
            )
        )
        await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def create_user_x_event_row(
        user_id: int,
        event_name: str,
        first_contact: str,
):
    """
    Create a new UserXEvent row.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.
        first_contact (str): Initial contact detail.

    Returns:
        None
    """
    async with async_session() as session:
        row = await get_user_x_event_row(user_id, event_name)
        if row == "not created":
            session.add(
                UserXEvent(
                    user_id=user_id,
                    event_name=event_name,
                    first_contact=first_contact,
                    status='reg',
                )
            )
            await session.commit()
        else:
            raise Error409


# --------------------------------------------------------------------------------
@db_error_handler
async def update_user_x_event_row_status(
        user_id: int,
        event_name: str,
        new_status: str,
) -> UserXEvent:
    """
    Update status of a UserXEvent row.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.
        new_status (str): New status value.

    Returns:
        UserXEvent: Updated row object.
    """
    async with async_session() as session:
        row = await get_user_x_event_row(user_id, event_name)
        if row == "not created":
            raise Error404
        setattr(row, 'status', new_status)
        session.add(row)
        await session.commit()
        return await get_user_x_event_row(user_id, event_name)


# --------------------------------------------------------------------------------
@db_error_handler
async def get_random_user_from_event(event_name: str):
    """
    Get random user ID from event with status 'been'.

    Args:
        event_name (str): Event name.

    Returns:
        int: Random user ID.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserXEvent.user_id)
            .where(
                and_(
                    UserXEvent.event_name == event_name,
                    UserXEvent.status == 'been',
                )
            )
            .order_by(func.random())
            .limit(1)
        )
        uid = result.scalar_one_or_none()
        if uid is None:
            raise Error404
        return uid


# --------------------------------------------------------------------------------
@db_error_handler
async def get_random_user_from_event_wth_bad(
        event_name: str,
        bad_ids: list[int],
) -> int:
    """
    Get random user ID excluding bad IDs.

    Args:
        event_name (str): Event name.
        bad_ids (list[int]): IDs to exclude.

    Returns:
        int: Random user ID.
    """
    async with async_session() as session:
        result = await session.execute(
            select(UserXEvent.user_id)
            .where(
                and_(
                    UserXEvent.event_name == event_name,
                    UserXEvent.status == 'been',
                    UserXEvent.user_id.notin_(bad_ids),
                )
            )
            .order_by(func.random())
            .limit(1)
        )
        uid = result.scalar_one_or_none()
        if uid is None:
            raise Error404
        return uid


# --------------------------------------------------------------------------------
@db_error_handler
async def get_users_tg_id_in_event(event_name: str):
    """
    Fetch IDs of users in event with status 'been'.

    Args:
        event_name (str): Event name.

    Returns:
        list[int]: List of user IDs.
    """
    async with async_session() as session:
        result = await session.execute(
            select(distinct(UserXEvent.user_id)).where(
                and_(
                    UserXEvent.event_name == event_name,
                    UserXEvent.status == 'been',
                )
            )
        )
        ids = result.scalars().all()
        if not ids:
            raise Error404
        return ids


# --------------------------------------------------------------------------------

@db_error_handler
async def get_users_tg_id_in_event_bad(event_name: str):
    """
    Retrieve distinct Telegram user IDs registered in an event.

    Args:
        event_name (str): Name of the event.

    Returns:
        list[int]: List of Telegram user IDs.
    """
    async with async_session() as session:
        users_tg_id = await session.execute(
            select(
                distinct(UserXEvent.user_id)
            ).where(
                and_(
                    UserXEvent.event_name == event_name,
                    UserXEvent.status == 'reg'
                )
            )
        )
        users_tg_ids = users_tg_id.scalars().all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


# --------------------------------------------------------------------------------

@db_error_handler
async def get_all_users_in_event(event_name: str):
    """
    Retrieve all users marked as 'been' for a given event.

    Args:
        event_name (str): Name of the event.

    Returns:
        list[tuple]: Tuples of UserXEvent and user handler.
    """
    async with async_session() as session:
        users = await session.execute(
            select(
                UserXEvent,
                User.handler
            ).join(
                UserXEvent,
                User.id == UserXEvent.user_id
            ).where(
                and_(
                    UserXEvent.status == 'been',
                    UserXEvent.event_name == event_name
                )
            )
        )
        users_tg_ids = users.all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


# --------------------------------------------------------------------------------

@db_error_handler
async def get_all_user_events(user_id: int):
    """
    Retrieve all in-progress events for a specific user.

    Args:
        user_id (int): Telegram user ID.

    Returns:
        list[Event]: List of Event objects in progress.
    """
    async with async_session() as session:
        query = (
            select(Event)
            .join(
                UserXEvent,
                Event.name == UserXEvent.event_name
            )
            .where(
                UserXEvent.user_id == user_id,
                Event.status == 'in_progress'
            )
        )
        result = await session.execute(query)
        events = result.scalars().all()
        if not events:
            raise Error404
        return events
