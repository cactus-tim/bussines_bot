"""
DB Operations

CRUD operations for users, club_events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
import datetime

from sqlalchemy import (select, delete)

from database.models import (
    async_session, FaceControl, )
from errors.errors import (
    Error409,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------

@db_error_handler
async def add_face_control(user_id: int, admin_id: int, username: str = None, full_name: str = None):
    """
    Add a new face control user.

    Args:
        user_id (int): Telegram ID of the user to add as face control
        admin_id (int): Telegram ID of the admin who is adding the user
        username (str, optional): Telegram username of the user
        full_name (str, optional): Full name of the user

    Returns:
        FaceControl: Created face control instance

    Raises:
        Error409: If user is already a face control
    """
    async with async_session() as session:
        # Check if user already exists as face control
        existing = await session.scalar(
            select(FaceControl).where(FaceControl.user_id == user_id)
        )
        if existing:
            raise Error409("User is already a face control")

        face_control = FaceControl(
            user_id=user_id,
            added_by=admin_id,
            added_at=datetime.datetime.utcnow().isoformat(),
            username=username,
            full_name=full_name
        )
        session.add(face_control)
        await session.commit()
        await session.refresh(face_control)
        return face_control


@db_error_handler
async def remove_face_control(user_id: int):
    """
    Remove a user from face control.

    Args:
        user_id (int): Telegram ID of the user to remove

    Returns:
        bool: True if user was removed, False if user wasn't a face control
    """
    async with async_session() as session:
        result = await session.execute(
            delete(FaceControl).where(FaceControl.user_id == user_id)
        )
        await session.commit()
        return result.rowcount > 0


@db_error_handler
async def get_face_control(user_id: int):
    """
    Get face control user by Telegram ID.

    Args:
        user_id (int): Telegram ID of the user

    Returns:
        FaceControl or str: Face control instance or "not found"
    """
    async with async_session() as session:
        face_control = await session.scalar(
            select(FaceControl).where(FaceControl.user_id == user_id)
        )
        if face_control:
            return face_control
        return "not found"


@db_error_handler
async def list_face_control():
    """
    List all face control users.

    Returns:
        list[FaceControl]: List of all face control users
    """
    async with async_session() as session:
        result = await session.execute(select(FaceControl))
        return list(result.scalars().all())
