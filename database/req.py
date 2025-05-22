"""
DB Operations

CRUD operations for users, events, vacancies, and networking.
"""

# --------------------------------------------------------------------------------
from sqlalchemy import (distinct, delete, func, select, and_, over)
from sqlalchemy.exc import NoResultFound
from datetime import datetime

from database.models import (
    Event,
    GiveAwayHost,
    Networking,
    Questionary,
    RegEvent,
    RefGiveAway,
    User,
    UserXEvent,
    Vacancy,
    QRCode,
    async_session, EventAttendance,
    FaceControl,
)
from errors.errors import (
    Error404,
    Error409,
    EventNameError,
    VacancyNameError,
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
            added_at=datetime.utcnow().isoformat(),
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


# --------------------------------------------------------------------------------
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
