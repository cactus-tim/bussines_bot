import pandas as pd
from io import BytesIO
from aiogram.types import BufferedInputFile

from database.req import get_all_users, get_all_users_in_event, get_all_quests
from bot_instance import bot
from errors.handlers import stat_error_handler


@stat_error_handler
async def get_stat_all(user_id: int):
    users = await get_all_users()
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
    data = [
        {
            "ID": user.id,
            "Handler": user.handler,
            "Is Superuser": user.is_superuser,
            "Status": (True if user.status == 'been' else False)
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
async def get_stat_quest(user_id: int):
    users = await get_all_quests()
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
