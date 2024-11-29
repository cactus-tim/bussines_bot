from sqlalchemy import select, desc, distinct, and_, func, delete
from sqlalchemy.exc import NoResultFound

from database.models import User, async_session, UserXEvent, Event, Questionary, Vacancy, RegEvent, RefGiveAway
from errors.errors import Error409, Error404, EventNameError, VacancyNameError
from errors.handlers import db_error_handler


@db_error_handler
async def get_user(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == tg_id))
        if user:
            return user
        else:
            return "not created"


@db_error_handler
async def create_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            data['id'] = tg_id
            user_data = User(**data)
            session.add(user_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_user(tg_id: int, data: dict):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        else:
            for key, value in data.items():
                setattr(user, key, value)
            session.add(user)
            await session.commit()


@db_error_handler
async def get_users_tg_id():
    async with async_session() as session:
        users_tg_id = await session.execute(select(distinct(User.id)))
        users_tg_ids = users_tg_id.scalars().all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_all_users():
    async with async_session() as session:
        users = await session.execute(select(User))
        users_tg_ids = users.scalars().all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_questionary(tg_id: int):
    async with async_session() as session:
        questionary = await session.scalar(select(Questionary).where(Questionary.user_id == tg_id))
        if questionary:
            return questionary
        else:
            return "not created"


@db_error_handler
async def create_questionary(tg_id: int):
    async with async_session() as session:
        questionary = await get_questionary(tg_id)
        data = {}
        if questionary == 'not created':
            data['user_id'] = tg_id
            user_data = Questionary(**data)
            session.add(user_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_questionary(tg_id: int, data: dict):
    async with async_session() as session:
        questionary = await get_questionary(tg_id)
        if questionary == 'not created':
            raise Error404
        else:
            for key, value in data.items():
                setattr(questionary, key, value)
            session.add(questionary)
            await session.commit()


@db_error_handler
async def get_all_quests():
    async with async_session() as session:
        quests = await session.execute(select(Questionary))
        quests_tg_ids = quests.scalars().all()
        if not quests_tg_ids:
            raise Error404
        return quests_tg_ids


@db_error_handler
async def get_event(name: str):
    async with async_session() as session:
        event = await session.scalar(select(Event).where(Event.name == name))
        if event:
            return event
        else:
            return "not created"


@db_error_handler
async def create_event(name: str, data: dict):
    async with async_session() as session:
        event = await get_event(name)
        if event == 'not created':
            data['name'] = name
            data['status'] = 'in_progress'
            user_data = Event(**data)
            session.add(user_data)
            await session.commit()
            return "all ok"
        else:
            raise EventNameError


@db_error_handler
async def update_event(name: str, data: dict):
    async with async_session() as session:
        event = await get_event(name)
        if event == 'not created':
            raise Error404
        else:
            for key, value in data.items():
                setattr(event, key, value)
            session.add(event)
            await session.commit()


@db_error_handler
async def get_all_events_in_p():
    async with async_session() as session:
        event = await session.execute(select(distinct(Event.name)).where(Event.status == "in_progress"))
        event_names = event.scalars().all()
        if not event_names:
            raise Error404
        return event_names


@db_error_handler
async def get_all_events():
    async with async_session() as session:
        event = await session.execute(select(distinct(Event.name)))
        event_names = event.scalars().all()
        if not event_names:
            raise Error404
        return event_names


@db_error_handler
async def get_vacancy(name: str):
    async with async_session() as session:
        vacancy = await session.scalar(select(Vacancy).where(Vacancy.name == name))
        if vacancy:
            return vacancy
        else:
            return "not created"


@db_error_handler
async def add_vacancy(name: str):
    async with async_session() as session:
        vacancy = await get_vacancy(name)
        data = {}
        if vacancy == 'not created':
            data['name'] = name
            user_data = Vacancy(**data)
            session.add(user_data)
            await session.commit()
            return "all ok"
        else:
            raise VacancyNameError


@db_error_handler
async def delete_vacancy(name: str):
    async with async_session() as session:
        vacancy = await get_vacancy(name)
        if vacancy == "not created":
            raise NoResultFound
        else:
            await session.delete(vacancy)
            await session.commit()
            return "all ok"


@db_error_handler
async def get_all_vacancy_names():
    async with async_session() as session:
        vacancy_names = await session.execute(select(distinct(Vacancy.name)))
        vacancy_names_clean = vacancy_names.scalars().all()
        if not vacancy_names_clean:
            raise Error404
        return vacancy_names_clean


@db_error_handler
async def get_user_x_event_row(user_id: int, event_name: str):
    async with async_session() as session:
        row = await session.scalar(select(UserXEvent).where(and_(
            UserXEvent.user_id == user_id,
            UserXEvent.event_name == event_name)))
        if row:
            return row
        else:
            return "not created"


@db_error_handler
async def delete_user_x_event_row(user_id: int, event_name: str):
    async with async_session() as session:
        await session.execute(
            delete(UserXEvent)
            .where(
                and_(
                    UserXEvent.user_id == user_id,
                    UserXEvent.event_name == event_name
                )
            )
        )
        await session.commit()


@db_error_handler
async def create_user_x_event_row(user_id: int, event_name: str, first_contact: str):
    async with async_session() as session:
        row = await get_user_x_event_row(user_id, event_name)
        data = {}
        if row == 'not created':
            data['user_id'] = user_id
            data['event_name'] = event_name
            data['first_contact'] = first_contact
            data['status'] = 'reg'
            user_x_event_data = UserXEvent(**data)
            session.add(user_x_event_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_user_x_event_row_status(user_id: int, event_name: str, new_status: str):
    async with async_session() as session:
        row = await get_user_x_event_row(user_id, event_name)
        if row == 'not created':
            raise Error404
        else:
            setattr(row, 'status', new_status)
            session.add(row)
            await session.commit()


@db_error_handler
async def get_random_user_from_event(event_name: str):
    async with async_session() as session:
        result = await session.execute(
            select(UserXEvent.user_id)
            .where(and_(
                UserXEvent.event_name == event_name,
                UserXEvent.status == 'been'
            ))
            .order_by(func.random())
            .limit(1)
        )
        random_user = result.scalar_one_or_none()
        if not random_user:
            raise Error404()
        return random_user


@db_error_handler
async def get_random_user_from_event_wth_bad(event_name: str, bad_ids: int):
    async with async_session() as session:
        result = await session.execute(
            select(UserXEvent.user_id)
            .where(and_(
                UserXEvent.event_name == event_name,
                UserXEvent.status == 'been',
                UserXEvent.user_id.notin_(bad_ids)
            ))
            .order_by(func.random())
            .limit(1)
        )
        random_user = result.scalar_one_or_none()
        if not random_user:
            raise Error404()
        return random_user


@db_error_handler
async def get_users_tg_id_in_event(event_name: str):
    async with async_session() as session:
        users_tg_id = await session.execute(select(distinct(UserXEvent.user_id)).where(and_(
            UserXEvent.event_name == event_name,
            UserXEvent.status == 'been'
        )))
        users_tg_ids = users_tg_id.scalars().all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_users_tg_id_in_event_bad(event_name: str):
    async with async_session() as session:
        users_tg_id = await session.execute(select(distinct(UserXEvent.user_id)).where(and_(
            UserXEvent.event_name == event_name,
            UserXEvent.status == 'reg'
        )))
        users_tg_ids = users_tg_id.scalars().all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_all_users_in_event(event_name: str):
    async with async_session() as session:
        users = await session.execute(
            select(UserXEvent, User.handler)
            .join(UserXEvent, User.id == UserXEvent.user_id)
            .where(and_(
                UserXEvent.status == 'been',
                UserXEvent.event_name == event_name))
        )
        users_tg_ids = users.all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_all_user_events(user_id: int):
    async with async_session() as session:
        query = (
            select(Event)
            .join(UserXEvent, Event.name == UserXEvent.event_name)
            .where(UserXEvent.user_id == user_id)
            .where(Event.status == 'in_progress')
        )
        result = await session.execute(query)
        events = result.scalars().all()
        if not events:
            raise Error404
        return events


@db_error_handler
async def get_reg_event(tg_id: int):
    async with async_session() as session:
        reg_event = await session.scalar(select(RegEvent).where(RegEvent.id == tg_id))
        if reg_event:
            return reg_event
        else:
            raise Error404


@db_error_handler
async def create_reg_event(tg_id: int):
    async with async_session() as session:
        reg_event = await get_reg_event(tg_id)
        if not reg_event:
            data = {'id': tg_id}
            reg_event_data = RegEvent(**data)
            session.add(reg_event_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def update_reg_event(tg_id: int, data: dict):
    async with async_session() as session:
        reg_event = await get_reg_event(tg_id)
        if not reg_event:
            raise Error404
        else:
            for key, value in data.items():
                setattr(reg_event, key, value)
            session.add(reg_event)
            await session.commit()


@db_error_handler
async def check_completly_reg_event(tg_id: int):
    async with async_session() as session:
        reg_event = await get_reg_event(tg_id)
        if not reg_event:
            return False
        if reg_event.name == '' or reg_event.surname == '' or reg_event.fathername == '' or reg_event.mail == '' or reg_event.phone == '' or reg_event.org == '':
            return False
        return True


@db_error_handler
async def get_ref_give_away(tg_id: int, event_name: str):
    async with async_session() as session:
        ref_give_away = await session.scalar(
            select(RefGiveAway)
            .where(
                and_(
                    RefGiveAway.user_id == tg_id,
                    RefGiveAway.event_name == event_name
                )))
        if not ref_give_away:
            raise Error404
        else:
            return ref_give_away


@db_error_handler
async def delete_ref_give_away_row(user_id: int, event_name: str):
    async with async_session() as session:
        await session.execute(
            delete(RefGiveAway)
            .where(
                and_(
                    RefGiveAway.user_id == user_id,
                    RefGiveAway.event_name == event_name
                )))
        await session.commit()


@db_error_handler
async def create_ref_give_away(tg_id: int, event_name: str, host_id: int):
    async with async_session() as session:
        ref_give_away = await get_ref_give_away(tg_id, event_name)
        if not ref_give_away:
            data = {'user_id': tg_id, 'event_name': event_name, 'host_id': host_id}
            ref_give_away_data = RefGiveAway(**data)
            session.add(ref_give_away_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def get_all_from_give_away(user_id: int, event_name: str):
    async with async_session() as session:
        users = await session.execute(
            select(RefGiveAway, User.handler)
            .join(RefGiveAway, User.id == RefGiveAway.user_id)
            .where(and_(
                RefGiveAway.host_id == user_id,
                RefGiveAway.event_name == event_name
            ))
        )
        users_tg_ids = users.all()
        if not users_tg_ids:
            raise Error404
        return users_tg_ids


@db_error_handler
async def get_reg_users(event_name: str):
    async with async_session() as session:
        users = await session.execute(
            select(RegEvent, User.handler)
            .join(UserXEvent, RegEvent.id == UserXEvent.user_id)
            .join(User, User.id == RegEvent.id)
            .where(UserXEvent.event_name == event_name)
        )
        users_data = users.all()
        if not users_data:
            raise Error404()
        return users_data


@db_error_handler
async def get_reg_users_stat(event_name: str):
    async with async_session() as session:
        users = await session.execute(
            select(UserXEvent, User.handler)
            .join(UserXEvent, User.id == UserXEvent.user_id)
            .where(UserXEvent.event_name == event_name)
        )
        users_data = users.all()
        if not users_data:
            raise Error404()
        return users_data


@db_error_handler
async def get_add_winner(host_id: int, event_name: str):
    async with async_session() as session:
        result = await session.execute(
            select(RefGiveAway.user_id)
            .join(UserXEvent, RefGiveAway.user_id == UserXEvent.user_id)
            .where(and_(
                RefGiveAway.host_id == host_id,
                RefGiveAway.event_name == event_name,
                UserXEvent.status == 'been'
            ))
            .order_by(func.random())
            .limit(1)
        )
        random_user = result.scalar_one_or_none()
        if not random_user:
            raise Error404()
        return random_user


@db_error_handler
async def get_users_unreg_tg_id(event_name: str):
    async with async_session() as session:
        result = await session.execute(
            select(User.id)
            .where(
                ~User.id.in_(
                    select(UserXEvent.user_id)
                    .where(UserXEvent.event_name == event_name)
                )
            )
        )
        users_data = result.scalars().all()
        if not users_data:
            raise Error404()
        return users_data
