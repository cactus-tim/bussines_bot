"""
DB Operations

CRUD operations for users, club_events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (distinct, select)
from sqlalchemy.exc import NoResultFound

from database.models import (
    Vacancy,
    async_session, )
from errors.errors import (
    Error404,
    VacancyNameError,
)
from errors.handlers import db_error_handler


# --------------------------------------------------------------------------------
@db_error_handler
async def get_vacancy(name: str):
    """
    Retrieve a vacancy by name.

    Args:
        name (str): Vacancy name.

    Returns:
        Vacancy or str: Vacancy object or "not created".
    """
    async with async_session() as session:
        vac = await session.scalar(
            select(Vacancy).where(Vacancy.name == name)
        )
        if vac:
            return vac
        return "not created"


# --------------------------------------------------------------------------------
@db_error_handler
async def add_vacancy(name: str):
    """
    Add a new vacancy.

    Args:
        name (str): Vacancy name.

    Returns:
        str: Confirmation message.
    """
    async with async_session() as session:
        vac = await get_vacancy(name)
        if vac == "not created":
            session.add(Vacancy(name=name))
            await session.commit()
            return "all ok"
        raise VacancyNameError


# --------------------------------------------------------------------------------
@db_error_handler
async def delete_vacancy(name: str):
    """
    Delete a vacancy by name.

    Args:
        name (str): Vacancy name.

    Returns:
        str: Confirmation message.
    """
    async with async_session() as session:
        vac = await get_vacancy(name)
        if vac == "not created":
            raise NoResultFound
        await session.delete(vac)
        await session.commit()
        return "all ok"


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_vacancy_names():
    """
    Fetch all distinct vacancy names.

    Returns:
        list[str]: List of vacancy names.
    """
    async with async_session() as session:
        result = await session.execute(
            select(distinct(Vacancy.name))
        )
        names = result.scalars().all()
        if not names:
            raise Error404
        return names
