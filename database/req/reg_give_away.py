"""
DB Operations

CRUD operations for users, events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (distinct, delete, func, select, and_)

from database.models import (
    GiveAwayHost,
    RegEvent,
    RefGiveAway,
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
async def get_ref_give_away(tg_id: int, event_name: str):
    """
    Retrieve a RefGiveAway record for a user in an event.

    Args:
        tg_id (int): Telegram user ID.
        event_name (str): Name of the event.

    Returns:
        RefGiveAway: Referral give-away data.
    """
    async with async_session() as session:
        ref_give_away = await session.scalar(
            select(RefGiveAway)
            .where(
                and_(
                    RefGiveAway.user_id == tg_id,
                    RefGiveAway.event_name == event_name
                )
            )
        )
        if not ref_give_away:
            raise Error404
        return ref_give_away


# --------------------------------------------------------------------------------

@db_error_handler
async def delete_ref_give_away_row(user_id: int, event_name: str):
    """
    Delete a RefGiveAway entry by user and event.

    Args:
        user_id (int): Telegram user ID.
        event_name (str): Name of the event.

    Returns:
        None
    """
    async with async_session() as session:
        await session.execute(
            delete(RefGiveAway)
            .where(
                and_(
                    RefGiveAway.user_id == user_id,
                    RefGiveAway.event_name == event_name
                )
            )
        )
        await session.commit()


# --------------------------------------------------------------------------------

@db_error_handler
async def create_ref_give_away(tg_id: int, event_name: str, host_id: int):
    """
    Create a new RefGiveAway entry for a user.

    Args:
        tg_id (int): Telegram user ID.
        event_name (str): Name of the event.
        host_id (int): Host user ID.

    Returns:
        None
    """
    async with async_session() as session:
        ref_give_away = await get_ref_give_away(tg_id, event_name)
        if not ref_give_away:
            data = {
                'user_id': tg_id,
                'event_name': event_name,
                'host_id': host_id
            }
            ref_give_away_data = RefGiveAway(**data)
            session.add(ref_give_away_data)
            await session.commit()
        else:
            raise Error409


# --------------------------------------------------------------------------------

@db_error_handler
async def get_all_from_give_away(user_id: int, event_name: str):
    """
    Retrieve all referrals given away by a host in an event.

    Args:
        user_id (int): Host Telegram user ID.
        event_name (str): Name of the event.

    Returns:
        list[tuple]: Tuples of RefGiveAway and user handler.
    """
    async with async_session() as session:
        users = await session.execute(
            select(
                RefGiveAway,
                User.handler
            ).join(
                RefGiveAway,
                User.id == RefGiveAway.user_id
            ).where(
                and_(
                    RefGiveAway.host_id == user_id,
                    RefGiveAway.event_name == event_name
                )
            )
        )
        users_tg_ids = users.all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


# --------------------------------------------------------------------------------

@db_error_handler
async def get_reg_users(event_name: str):
    """
    Retrieve registered users and handlers for an event.

    Args:
        event_name (str): Name of the event.

    Returns:
        list[tuple]: Tuples of RegEvent and user handler.
    """
    async with async_session() as session:
        users = await session.execute(
            select(
                RegEvent,
                User.handler
            ).join(
                UserXEvent,
                RegEvent.id == UserXEvent.user_id
            ).join(
                User,
                User.id == RegEvent.id
            ).where(
                UserXEvent.event_name == event_name
            )
        )
        users_data = users.all()
        if not users_data:
            raise Error404
        return users_data


# --------------------------------------------------------------------------------

@db_error_handler
async def get_reg_users_stat(event_name: str):
    """
    Retrieve user registration statistics for an event.

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
                UserXEvent.event_name == event_name
            )
        )
        users_data = users.all()
        if not users_data:
            raise Error404
        return users_data


# --------------------------------------------------------------------------------

@db_error_handler
async def get_add_winner(host_id: int, event_name: str):
    """
    Select a random winner from a host's referrals who attended an event.

    Args:
        host_id (int): Host Telegram user ID.
        event_name (str): Name of the event.

    Returns:
        int: Telegram user ID of the winner.
    """
    async with async_session() as session:
        result = await session.execute(
            select(
                RefGiveAway.user_id
            ).join(
                UserXEvent,
                RefGiveAway.user_id == UserXEvent.user_id
            ).where(
                and_(
                    RefGiveAway.host_id == host_id,
                    RefGiveAway.event_name == event_name,
                    UserXEvent.status == 'been'
                )
            ).order_by(
                func.random()
            ).limit(1)
        )
        random_user = result.scalar_one_or_none()
        if not random_user:
            raise Error404
        return random_user


# --------------------------------------------------------------------------------

@db_error_handler
async def get_users_unreg_tg_id(event_name: str):
    """
    Retrieve IDs of users not registered in an event.

    Args:
        event_name (str): Name of the event.

    Returns:
        list[int]: List of unregistered Telegram user IDs.
    """
    async with async_session() as session:
        result = await session.execute(
            select(
                User.id
            ).where(
                ~User.id.in_(
                    select(UserXEvent.user_id)
                    .where(UserXEvent.event_name == event_name)
                )
            )
        )
        users_data = result.scalars().all()
        if not users_data:
            raise Error404
        return users_data


# --------------------------------------------------------------------------------

@db_error_handler
async def get_host(user_id: int, event_name: str):
    """
    Retrieve a GiveAwayHost entry by user and event.

    Args:
        user_id (int): Telegram user ID of the host.
        event_name (str): Name of the event.

    Returns:
        GiveAwayHost: Host data for the event.
    """
    async with async_session() as session:
        host = await session.scalar(
            select(GiveAwayHost).where(
                and_(
                    GiveAwayHost.user_id == user_id,
                    GiveAwayHost.event_name == event_name
                )
            )
        )
        if host:
            return host
        else:
            raise Error404


# --------------------------------------------------------------------------------

@db_error_handler
async def get_host_by_org_name(org_name: str, event_name: str):
    """
    Retrieve host by organization and event names.

    Args:
        org_name (str): Organization name.
        event_name (str): Event name.

    Returns:
        GiveAwayHost: Host instance.

    Raises:
        Error404: If host not found.
    """
    async with async_session() as session:
        host = await session.scalar(
            select(GiveAwayHost)
            .where(
                and_(
                    GiveAwayHost.org_name == org_name,
                    GiveAwayHost.event_name == event_name,
                )
            ),
        )
        if host:
            return host
        else:
            raise Error404


# --------------------------------------------------------------------------------
@db_error_handler
async def create_host(user_id: int, event_name: str, org_name: str):
    """
    Create a new host record if none exists.

    Args:
        user_id (int): User identifier.
        event_name (str): Event name.
        org_name (str): Organization name.

    Raises:
        Error409: If host already exists.
    """
    async with async_session() as session:
        host = await get_host(user_id)
        if not host:
            data = {
                'user_id': user_id,
                'event_name': event_name,
                'org_name': org_name,
            }
            host_data = GiveAwayHost(**data)
            session.add(host_data)
            await session.commit()
        else:
            raise Error409


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_hosts_in_event_ids(event_name: str):
    """
    Retrieve all host user IDs for an event.

    Args:
        event_name (str): Event name.

    Returns:
        list[int]: List of user IDs.

    Raises:
        Error404: If no hosts found.
    """
    async with async_session() as session:
        hosts_ids = await session.execute(
            select(distinct(GiveAwayHost.user_id))
            .where(GiveAwayHost.event_name == event_name),
        )
        hosts = hosts_ids.scalars().all()
        if not hosts:
            raise Error404
        return hosts


# --------------------------------------------------------------------------------
@db_error_handler
async def get_all_hosts_in_event_orgs(event_name: str):
    """
    Retrieve all host organization names for an event.

    Args:
        event_name (str): Event name.

    Returns:
        list[str]: List of organization names.

    Raises:
        Error404: If no hosts found.
    """
    async with async_session() as session:
        hosts_ids = await session.execute(
            select(distinct(GiveAwayHost.org_name))
            .where(GiveAwayHost.event_name == event_name),
        )
        hosts = hosts_ids.scalars().all()
        if not hosts:
            raise Error404
        return hosts
