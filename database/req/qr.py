"""
DB Operations

CRUD operations for users, events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (select, and_)

from database.models import (
    QRCode,
    async_session, EventAttendance,
)
from errors.handlers import db_error_handler


@db_error_handler
async def create_qr_code(user_id: int, event_name: str):
    """
    Create a new QR code for a user and event.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.

    Returns:
        QRCode: Created QR code instance.
    """
    async with async_session() as session:
        from datetime import datetime
        qr_code = QRCode(
            user_id=user_id,
            event_name=event_name,
            created_at=datetime.utcnow().isoformat(),
            is_used=False
        )
        session.add(qr_code)
        await session.commit()
        await session.refresh(qr_code)
        return qr_code


# --------------------------------------------------------------------------------
@db_error_handler
async def get_latest_qr_code(user_id: int):
    """
    Get the latest QR code for a user.

    Args:
        user_id (int): Telegram user identifier.

    Returns:
        QRCode or None: Latest QR code instance or None if not found.
    """
    async with async_session() as session:
        result = await session.execute(
            select(QRCode)
            .where(QRCode.user_id == user_id)
            .order_by(QRCode.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


# --------------------------------------------------------------------------------
@db_error_handler
async def mark_qr_code_used(qr_code_id: int):
    """
    Mark a QR code as used.

    Args:
        qr_code_id (int): QR code identifier.

    Returns:
        None
    """
    async with async_session() as session:
        qr_code = await session.get(QRCode, qr_code_id)
        if qr_code:
            qr_code.is_used = True
            await session.commit()


# --------------------------------------------------------------------------------
@db_error_handler
async def record_attendance(user_id: int, event_name: str, verified_by: int):
    """
    Record user attendance at an event.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.
        verified_by (int): Telegram ID of the superuser who verified.

    Returns:
        EventAttendance: Created attendance record.
    """
    async with async_session() as session:
        from datetime import datetime
        attendance = EventAttendance(
            user_id=user_id,
            event_name=event_name,
            attended_at=datetime.utcnow().isoformat(),
            verified_by=verified_by
        )
        session.add(attendance)
        await session.commit()
        await session.refresh(attendance)
        return attendance


# --------------------------------------------------------------------------------
@db_error_handler
async def get_user_attendance(user_id: int, event_name: str):
    """
    Check if a user has attended an event.

    Args:
        user_id (int): Telegram user identifier.
        event_name (str): Event name.

    Returns:
        EventAttendance or None: Attendance record if found, None otherwise.
    """
    async with async_session() as session:
        result = await session.execute(
            select(EventAttendance)
            .where(
                and_(
                    EventAttendance.user_id == user_id,
                    EventAttendance.event_name == event_name
                )
            )
        )
        return result.scalar_one_or_none()
