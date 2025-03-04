import pandas as pd
from io import BytesIO
from aiogram.types import BufferedInputFile

from database.req import get_all_users, get_all_users_in_event, get_all_quests, get_all_from_give_away, get_reg_users_stat, get_reg_users
from bot_instance import bot
from errors.handlers import stat_error_handler
from handlers.error import safe_send_message


@stat_error_handler
async def get_stat_all(user_id: int):
    users = await get_all_users()
    if not users:
        await safe_send_message(bot, user_id, 'У вас нет подходяших пользователей((')
    data = [
        {
            "ID": user.id,
            "Handler": user.handler,
            "Is Superuser": user.is_superuser,
            "Event Count": user.event_cnt,
            "Strick": user.strick
        }
        for user in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(buffer.read(), filename="user_statistics.xlsx")
        await bot.send_document(user_id, temp_file)


@stat_error_handler
async def get_stat_all_in_ev(user_id: int, event_name: str):
    users = await get_all_users_in_event(event_name)
    if not users:
        await safe_send_message(bot, user_id, 'У вас нет подходяших пользователей((')
    data = []
    cnt = {}
    cntt = 0
    for user_x_event, handler in users:
        data.append({
            'User_id': user_x_event.user_id,
            "Handler": handler,
            'Event_name': user_x_event.event_name,
            'Status': user_x_event.status,
            'First_contact': user_x_event.first_contact,
        })
        if user_x_event.first_contact not in cnt:
            cnt[user_x_event.first_contact] = 0
        cnt[user_x_event.first_contact] += 1
        cntt += 1

    msg = ''.join(
        (f'С потока {key} зарегистировалось человек: {value}, это {(value / cntt) * 100:.1f}% от общего трафика\n' for
         key, value in cnt.items()))
    msg += f'Всего зарегистировалось человек: {cntt} человек'
    # TODO: not important: think about replace 'flow n' to normal flow name
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(buffer.read(), filename="user_statistics.xlsx")
        await safe_send_message(bot, user_id, msg)
        await bot.send_document(user_id, temp_file)


@stat_error_handler
async def get_stat_quest(user_id: int):
    users = await get_all_quests()
    if not users:
        await safe_send_message(bot, user_id, 'У вас нет подходяших пользователей((')
    data = [
        {
            "ID": user.user_id,
            "full_name": user.full_name,
            "degree": user.degree,
            "course": user.course,
            "program": user.program,
            "email": user.email,
            "vacancy": user.vacancy,
            "motivation": user.motivation,
            "plans": user.plans,
            "strengths": user.strengths,
            "career_goals": user.career_goals,
            "team_motivation": user.team_motivation,
            "role_in_team": user.role_in_team,
            "events": user.events,
            "found_info": user.found_info,
            "resume": user.resume,
        }
        for user in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(buffer.read(), filename="user_statistics.xlsx")
        await bot.send_document(user_id, temp_file)


@stat_error_handler
async def get_stat_ad_give_away(user_id: int, host_id: int, event_name: str):
    users = await get_all_from_give_away(host_id, event_name)
    if not users:
        await safe_send_message(bot, user_id, 'У вас нет подходяших пользователей((')
    data = [
        {
            "ID": user.user_id,
            "Handler": handler,
            "Event": user.event_name
        }
        for user, handler in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(buffer.read(), filename="user_statistics.xlsx")
        await bot.send_document(user_id, temp_file)


@stat_error_handler
async def get_stat_reg_out(user_id: int, event_name: str):
    users = await get_reg_users(event_name)
    if not users:
        await safe_send_message(bot, user_id, 'У вас нет подходяших пользователей((')
    data = [
        {
            'Id': user.id,
            "Handler": handler,
            'Name': user.name,
            'Surname': user.surname,
            'Fathername': user.fathername,
            'Mail': user.mail,
            'Phone': user.phone,
            'Organization': user.org
        }
        for user, handler in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(buffer.read(), filename="user_statistics.xlsx")
        await bot.send_document(user_id, temp_file)


@stat_error_handler
async def get_stat_reg(user_id: int, event_name: str):
    users = await get_reg_users_stat(event_name)
    if not users:
        await safe_send_message(bot, user_id, 'У вас нет подходяших пользователей((')
    data = []
    cnt = {}
    cntt = 0
    for user_x_event, handler in users:
        data.append({
                'User_id': user_x_event.user_id,
                "Handler": handler,
                'Event_name': user_x_event.event_name,
                'Status': user_x_event.status,
                'First_contact': user_x_event.first_contact,
        })
        if user_x_event.first_contact not in cnt:
            cnt[user_x_event.first_contact] = 0
        cnt[user_x_event.first_contact] += 1
        cntt += 1

    msg = ''.join((f'С потока {key} зарегистировалось человек: {value}, это {(value / cntt) * 100:.1f}% от общего трафика\n' for key, value in cnt.items()))
    msg += f'Всего зарегистировалось человек: {cntt}'
    # TODO: not important: think about replace 'flow n' to normal flow name
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(buffer.read(), filename="user_statistics.xlsx")
        await safe_send_message(bot, user_id, msg)
        await bot.send_document(user_id, temp_file)
