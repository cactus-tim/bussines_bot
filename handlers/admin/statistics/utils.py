"""
Statistics Handlers
Excel export of user statistics for bot.
"""

# --------------------------------------------------------------------------------
from io import BytesIO

import pandas as pd
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BufferedInputFile
from sqlalchemy.sql import select

from config.settings import TOKEN
from database.models import async_session, UserXEvent, Event
from database.req import (
    get_all_users,
    get_all_users_in_event,
    get_all_quests,
    get_all_from_give_away,
    get_reg_users_stat,
    get_reg_users,
)
from errors.errors import Error404
from errors.handlers import stat_error_handler
from handlers.error import safe_send_message

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)


# --------------------------------------------------------------------------------
@stat_error_handler
async def get_stat_all(user_id: int) -> None:
    """
    Retrieve all users and send statistics as Excel.

    Args:
        user_id (int): Telegram user ID to send report.

    Returns:
        None
    """
    users = await get_all_users()
    if not users:
        await safe_send_message(
            bot, user_id, 'У вас нет подходящих пользователей((')
        return

    # Get all events for each user
    data = []
    for user in users:
        try:
            # Get all events where user has status 'been'
            async with async_session() as session:
                result = await session.execute(
                    select(
                        Event,
                        UserXEvent.status,
                        UserXEvent.first_contact
                    ).join(
                        UserXEvent,
                        Event.name == UserXEvent.event_name
                    ).where(
                        UserXEvent.user_id == user.id,
                        UserXEvent.status == 'been'
                    ).order_by(Event.date.desc())
                )
                visited_events = result.all()

                # Format visited events info
                visited_events_info = []
                for event, status, first_contact in visited_events:
                    visited_events_info.append(
                        f"{event.desc} ({event.date} {event.time})"
                    )

                visited_events_str = "\n".join(
                    visited_events_info) if visited_events_info else "Нет посещенных мероприятий"
        except Error404:
            visited_events_str = "Нет посещенных мероприятий"

        data.append({
            "ID": user.id,
            "Handler": user.handler,
            "Is Superuser": user.is_superuser,
            "Event Count": user.event_cnt,
            "Strick": user.strick,
            "Money": user.money,
            "Referral Count": user.ref_cnt,
            "Visited Events": visited_events_str
        })

    df = pd.DataFrame(data)

    # Adjust column widths for better readability
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
            worksheet = writer.sheets["Users"]
            worksheet.set_column('A:A', 10)  # ID
            worksheet.set_column('B:B', 20)  # Handler
            worksheet.set_column('C:C', 12)  # Is Superuser
            worksheet.set_column('D:D', 12)  # Event Count
            worksheet.set_column('E:E', 10)  # Strick
            worksheet.set_column('F:F', 10)  # Money
            worksheet.set_column('G:G', 15)  # Referral Count
            worksheet.set_column('H:H', 50)  # Visited Events

        buffer.seek(0)
        temp_file = BufferedInputFile(
            buffer.read(), filename="user_statistics.xlsx"
        )
        await bot.send_document(user_id, temp_file)


# --------------------------------------------------------------------------------
@stat_error_handler
async def get_stat_all_in_ev(user_id: int, event_name: str) -> None:
    """
    Retrieve users in event and send Excel plus summary.

    Args:
        user_id (int): Telegram user ID to send report.
        event_name (str): Event identifier.

    Returns:
        None
    """
    users = await get_all_users_in_event(event_name)
    if not users:
        await safe_send_message(
            bot, user_id, 'У вас нет подходящих пользователей((')
        return
    data = []
    cnt: dict[str, int] = {}
    total = 0
    for ue, handler in users:
        data.append({
            'User_id': ue.user_id,
            'Handler': handler,
            'Event_name': ue.event_name,
            'Status': ue.status,
            'First_contact': ue.first_contact,
        })
        cnt[ue.first_contact] = cnt.get(ue.first_contact, 0) + 1
        total += 1
    msg = ''.join(
        (
            f'С потока {key} зарегистрировалось человек: {value}, '
            f'это {(value / total) * 100:.1f}% от общего трафика\n'
        ) for key, value in cnt.items()
    )
    msg += f'Всего зарегистрировалось человек: {total} человек'
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(
            buffer.read(), filename="user_statistics.xlsx"
        )
        await safe_send_message(bot, user_id, msg)
        await bot.send_document(user_id, temp_file)


# --------------------------------------------------------------------------------
@stat_error_handler
async def get_stat_quest(user_id: int) -> None:
    """
    Retrieve questionnaire submissions and send as Excel.

    Args:
        user_id (int): Telegram user ID to send report.

    Returns:
        None
    """
    users = await get_all_quests()
    if not users:
        await safe_send_message(
            bot, user_id, 'У вас нет подходящих пользователей((')
        return
    data = [
        {
            "ID": u.user_id,
            "full_name": u.full_name,
            "degree": u.degree,
            "course": u.course,
            "program": u.program,
            "email": u.email,
            "vacancy": u.vacancy,
            "motivation": u.motivation,
            "plans": u.plans,
            "strengths": u.strengths,
            "career_goals": u.career_goals,
            "team_motivation": u.team_motivation,
            "role_in_team": u.role_in_team,
            "events": u.events,
            "found_info": u.found_info,
            "resume": u.resume,
        }
        for u in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(
            buffer.read(), filename="user_statistics.xlsx"
        )
        await bot.send_document(user_id, temp_file)


# --------------------------------------------------------------------------------
@stat_error_handler
async def get_stat_ad_give_away(
        user_id: int,
        host_id: int,
        event_name: str,
) -> None:
    """
    Retrieve giveaway participants and send as Excel.

    Args:
        user_id (int): Telegram user ID to send report.
        host_id (int): Host identifier.
        event_name (str): Event identifier.

    Returns:
        None
    """
    users = await get_all_from_give_away(host_id, event_name)
    if not users:
        await safe_send_message(
            bot, user_id, 'У вас нет подходящих пользователей((')
        return
    data = [
        {
            "ID": u.user_id,
            "Handler": h,
            "Event": u.event_name,
        }
        for u, h in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(
            buffer.read(), filename="user_statistics.xlsx"
        )
        await bot.send_document(user_id, temp_file)


# --------------------------------------------------------------------------------
@stat_error_handler
async def get_stat_reg_out(user_id: int, event_name: str) -> None:
    """
    Retrieve external registrations and send as Excel.

    Args:
        user_id (int): Telegram user ID to send report.
        event_name (str): Event identifier.

    Returns:
        None
    """
    users = await get_reg_users(event_name)
    if not users:
        await safe_send_message(
            bot, user_id, 'У вас нет подходящих пользователей((')
        return
    data = [
        {
            'Id': u.id,
            'Handler': h,
            'Name': u.name,
            'Surname': u.surname,
            'Fathername': u.fathername,
            'Mail': u.mail,
            'Phone': u.phone,
            'Organization': u.org,
        }
        for u, h in users
    ]
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(
            buffer.read(), filename="user_statistics.xlsx"
        )
        await bot.send_document(user_id, temp_file)


# --------------------------------------------------------------------------------
@stat_error_handler
async def get_stat_reg(user_id: int, event_name: str) -> None:
    """
    Retrieve registration statistics and send Excel plus summary.

    Args:
        user_id (int): Telegram user ID to send report.
        event_name (str): Event identifier.

    Returns:
        None
    """
    users = await get_reg_users_stat(event_name)
    if not users:
        await safe_send_message(
            bot, user_id, 'У вас нет подходящих пользователей((')
        return
    data = []
    cnt: dict[str, int] = {}
    total = 0
    for ue, h in users:
        data.append({
            'User_id': ue.user_id,
            'Handler': h,
            'Event_name': ue.event_name,
            'Status': ue.status,
            'First_contact': ue.first_contact,
        })
        cnt[ue.first_contact] = cnt.get(ue.first_contact, 0) + 1
        total += 1
    msg = ''.join(
        (
            f'С потока {key} зарегистрировалось человек: {value}, '
            f'это {(value / total) * 100:.1f}% от общего трафика\n'
        ) for key, value in cnt.items()
    )
    msg += f'Всего зарегистрировалось человек: {total}'
    df = pd.DataFrame(data)
    with BytesIO() as buffer:
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="Users")
        buffer.seek(0)
        temp_file = BufferedInputFile(
            buffer.read(), filename="user_statistics.xlsx"
        )
        await safe_send_message(bot, user_id, msg)
        await bot.send_document(user_id, temp_file)
