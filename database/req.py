from sqlalchemy import select, desc, distinct, and_, func, delete, over
from sqlalchemy.exc import NoResultFound

from database.models import User, async_session, UserXEvent, Event, Questionary, Vacancy, RegEvent, RefGiveAway, GiveAwayHost, Networking
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
            return user_data
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
        row = await get_user_x_event_row(user_id, event_name)
        return row


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


@db_error_handler
async def get_host(user_id: int, event_name: str):
    async with async_session() as session:
        host = await session.scalar(
            select(GiveAwayHost)
            .where(and_(
                GiveAwayHost.user_id == user_id,
                GiveAwayHost.event_name == event_name
            )))
        if host:
            return host
        else:
            raise Error404


@db_error_handler
async def get_host_by_org_name(org_name: str, event_name: str):
    async with async_session() as session:
        host = await session.scalar(
            select(GiveAwayHost)
            .where(and_(
                GiveAwayHost.org_name == org_name,
                GiveAwayHost.event_name == event_name
            )))
        if host:
            return host
        else:
            raise Error404


@db_error_handler
async def create_host(user_id: int, event_name: str, org_name: str):
    async with async_session() as session:
        host = await get_host(user_id)
        if not host:
            data = {
                'user_id': user_id,
                'event_name': event_name,
                'org_name': org_name
            }
            host_data = GiveAwayHost(**data)
            session.add(host_data)
            await session.commit()
        else:
            raise Error409


@db_error_handler
async def get_all_hosts_in_event_ids(event_name: str):
    async with async_session() as session:
        hosts_ids = await session.execute(
            select(distinct(GiveAwayHost.user_id))
            .where(GiveAwayHost.event_name == event_name)
        )
        hosts = hosts_ids.scalars().all()
        if not hosts:
            raise Error404
        return hosts


@db_error_handler
async def get_all_hosts_in_event_orgs(event_name: str):
    async with async_session() as session:
        hosts_ids = await session.execute(
            select(distinct(GiveAwayHost.org_name))
            .where(GiveAwayHost.event_name == event_name)
        )
        hosts = hosts_ids.scalars().all()
        if not hosts:
            raise Error404
        return hosts


@db_error_handler
async def add_money(tg_id: int, cnt: int):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        else:
            setattr(user, 'money', user.money + cnt)
            session.add(user)
            await session.commit()


@db_error_handler
async def one_more_event(tg_id: int):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        else:
            setattr(user, 'event_cnt', user.event_cnt + 1)
            session.add(user)
            await session.commit()


@db_error_handler
async def add_referal_cnt(tg_id: int):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        else:
            setattr(user, 'ref_cnt', user.ref_cnt + 1)
            session.add(user)
            await session.commit()


@db_error_handler
async def update_strick(tg_id: int, cnt: id = 1):
    async with async_session() as session:
        user = await get_user(tg_id)
        if user == 'not created':
            raise Error404
        else:
            if cnt == 0:
                setattr(user, 'strick', 0)
            else:
                setattr(user, 'strick', user.strick + 1)
            session.add(user)
            await session.commit()


@db_error_handler
async def get_user_rank_by_money(specific_user_id: int) -> int:
    async with async_session() as session:
        rank_column = over(func.row_number(), order_by=User.money.desc()).label('rank')
        subquery = (
            select(User.id, rank_column)
            .subquery()
        )
        query = select(subquery.c.rank).where(subquery.c.id == specific_user_id)
        result = await session.execute(query)
        user_rank = result.scalar()
        if user_rank is None:
            raise Error404

        return user_rank


@db_error_handler
async def get_top_10_users_by_money() -> list[User]:
    async with async_session() as session:
        query = (
            select(User)
            .order_by(User.money.desc())
            .limit(10)
        )
        result = await session.execute(query)
        top_users = result.scalars().all()
        return top_users


@db_error_handler
async def add_user_to_networking(tg_id: int):
    async with async_session() as session:
        existing_user = await session.scalar(select(Networking).where(Networking.id == tg_id))
        if existing_user:
            raise Error409
        networking = Networking(id=tg_id)
        session.add(networking)
        await session.commit()
        return 'ok'


@db_error_handler
async def get_all_for_networking():
    async with async_session() as session:
        networking = await session.execute(select(Networking.id))
        networking_data = networking.scalars().all()
        if not networking_data:
            raise Error404
        return networking_data


@db_error_handler
async def delete_all_from_networking():
    async with async_session() as session:
        await session.execute(delete(Networking))
        await session.commit()
