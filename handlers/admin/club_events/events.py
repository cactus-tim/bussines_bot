"""
Event Management Bot
Handles event creation, linking, and participant selection in Telegram.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from config.texts.months import MONTHS
from database.req import (
    get_user, update_event, create_event,
    get_all_events_in_p, get_random_user_from_event,
    get_users_tg_id_in_event, get_random_user_from_event_wth_bad,
    get_users_tg_id_in_event_bad, update_user_x_event_row_status,
    update_strick
)
from handlers.error import safe_send_message
from handlers.states import EventCreateState, EventState
from handlers.utils.base import get_bot_username
from keyboards import main_reply_keyboard, post_ev_target, apply_winner
from utils.validators import is_number_in_range, is_valid_time_format

# --------------------------------------------------------------------------------

router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# --------------------------------------------------------------------------------

@router.message(Command("add_event"))
async def cmd_add_event(message: Message, state: FSMContext):
    """
    Starts the event creation process.

    Args:
        message (Message): The command message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, "Введите полное название события")
    await state.set_state(EventCreateState.waiting_event_name)


# --------------------------------------------------------------------------------

@router.message(EventCreateState.waiting_event_name)
async def add_event_part_2(message: Message, state: FSMContext):
    """
    Saves event description and requests event date.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await state.update_data({'desc': message.text})
    await safe_send_message(bot, message, "Введите дату проведения события в формате DD.MM.YY")
    await state.set_state(EventCreateState.waiting_event_date)


# --------------------------------------------------------------------------------

@router.message(EventCreateState.waiting_event_date)
async def add_event_part_3(message: Message, state: FSMContext):
    """
    Saves event date, creates event, and requests time.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    data = await state.get_data()
    desc = data.get('desc')
    name = "event" + message.text.replace('.', '_')
    dat = (message.text.split('.')[0].lstrip('0')) + MONTHS[int(message.text.split('.')[1].lstrip('0'))]

    await create_event(name, {'desc': desc, 'date': dat})
    await safe_send_message(bot, message, 'Отправьте время проведение мероприятия')
    await state.update_data({'name': name})
    await state.set_state(EventCreateState.waiting_event_time)


# --------------------------------------------------------------------------------

@router.message(EventCreateState.waiting_event_time)
async def add_event_part_4(message: Message, state: FSMContext):
    """
    Saves event time and requests place.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    data = await state.get_data()
    name = data.get('name')

    if not is_valid_time_format(message.text):
        await safe_send_message(bot, message,
                                'Неверный формат времени. Пожалуйста, используйте формат HH:MM (например, 14:30)')
        return

    await update_event(name, {'time': message.text})
    await safe_send_message(bot, message, 'Отправьте место проведение мероприятия')
    await state.set_state(EventCreateState.waiting_event_place)


# --------------------------------------------------------------------------------

@router.message(EventCreateState.waiting_event_place)
async def add_event_part_5(message: Message, state: FSMContext):
    """
    Saves event place and requests link count.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    data = await state.get_data()
    name = data.get('name')
    await update_event(name, {'place': message.text})
    await safe_send_message(bot, message, 'Введи количество ссылок для регистрации, которое вам нужно')
    await state.set_state(EventCreateState.waiting_links_count)


# --------------------------------------------------------------------------------

@router.message(EventCreateState.waiting_links_count)
async def add_event_part_6(message: Message, state: FSMContext):
    """
    Generates registration and confirmation links.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    data = await state.get_data()
    name = data.get('name')
    links = ''

    bot_username = await get_bot_username()
    if not await is_number_in_range(message.text):
        await safe_send_message(bot, message, 'Введи число от 1 до 20')
        return

    for i in range(1, int(message.text) + 1):
        data1 = f'reg_{name}_{i}'
        links += f"https://t.me/{bot_username}?start={data1}\n"
    data2 = name
    url2 = f"https://t.me/{bot_username}?start={data2}"

    await safe_send_message(bot, message, f"все круто, все создано!!\nссылки для регистрации:"
                                          f"\n{links}"
                                          f"\nссылка для подтверждения:"
                                          f"\n{url2}", reply_markup=main_reply_keyboard())
    await state.clear()


# --------------------------------------------------------------------------------

@router.message(Command("end_event"))
async def cmd_end_event(message: Message, state: FSMContext):
    """
    Begins event completion process.

    Args:
        message (Message): The command message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return

    events = await get_all_events_in_p()
    if not events:
        await safe_send_message(bot, message, "Нет активных событий(")
        return

    await safe_send_message(bot, message, text="Выберете событие", reply_markup=post_ev_target(events))
    await state.set_state(EventState.waiting_ev)


# --------------------------------------------------------------------------------

@router.message(EventState.waiting_ev)
async def process_end_event(message: Message, state: FSMContext):
    """
    Selects a winner and starts verification.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    user_id = await get_random_user_from_event(message.text)
    await state.update_data(event_name=message.text)
    await state.update_data(user_id=user_id)
    await state.update_data(bad_ids=[])

    user = await get_user(user_id)
    if user == "not created":
        await safe_send_message(bot, message, text="Какие то проблемы, попробуйте заново")
        await state.clear()
        return

    await safe_send_message(bot, message, text=f"Предварительный победитель - @{user.handler}, проверьте его наличие в "
                                               f"аудитории", reply_markup=apply_winner())


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "reroll")
async def reroll_end_event(callback: CallbackQuery, state: FSMContext):
    """
    Selects another winner if previous is invalid.

    Args:
        callback (CallbackQuery): The callback query.
        state (FSMContext): The state context.

    Returns:
        None
    """
    data = await state.get_data()
    bad_ids = data.get("bad_ids")
    user_id = data.get("user_id")
    event_name = data.get("event_name")

    bad_ids.append(user_id)
    user_id = await get_random_user_from_event_wth_bad(event_name, bad_ids)
    await state.update_data(bad_ids=bad_ids)
    await state.update_data(user_id=user_id)

    user = await get_user(user_id)
    if user == "not created":
        await safe_send_message(bot, callback, text="Какие то проблемы, попробуйте заново")
        await state.clear()
        return

    await safe_send_message(bot, callback,
                            text=f"Предварительный победитель - @{user.handler}, проверьте его наличие в "
                                 f"аудитории", reply_markup=apply_winner())


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "confirm")
async def confirm_end_event(callback: CallbackQuery, state: FSMContext):
    """
    Confirms winner and notifies participants.

    Args:
        callback (CallbackQuery): The callback query.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await safe_send_message(bot, callback, text="Отличное, рассылаю все информацию")
    data = await state.get_data()
    event_name = data.get("event_name")
    user_id = data.get("user_id")

    await update_event(event_name, {'winner': user_id, "status": "end"})
    user = await get_user(user_id)
    user_ids = await get_users_tg_id_in_event(event_name)

    if not user_ids:
        await safe_send_message(bot, user_id, text="У вас нет пользователей))",
                                reply_markup=main_reply_keyboard())
    else:
        for uid in user_ids:
            await safe_send_message(bot, uid, text=f"Сегодняшний победитель - @{user.handler}",
                                    reply_markup=main_reply_keyboard())

    bad_user_ids = await get_users_tg_id_in_event_bad(event_name)
    if bad_user_ids:
        for uid in bad_user_ids:
            await update_strick(uid, 0)
            await update_user_x_event_row_status(uid, event_name, 'nbeen')

    await safe_send_message(bot, callback, 'Готово')
    await state.clear()


# --------------------------------------------------------------------------------

@router.message(Command("get_link"))
async def get_link(message: Message, state: FSMContext):
    """
    Starts process to generate new registration links.

    Args:
        message (Message): The command message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return

    events = await get_all_events_in_p()
    if not events:
        await safe_send_message(bot, message, 'У вас нет событий((')
        return

    await safe_send_message(bot, message, text="Выберете событие", reply_markup=post_ev_target(events))
    await state.set_state(EventState.waiting_ev_for_link)


# --------------------------------------------------------------------------------

@router.message(EventState.waiting_ev_for_link)
async def make_link_05(message: Message, state: FSMContext):
    """
    Saves selected event name and requests link count.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    await state.update_data({'name': message.text})
    await safe_send_message(bot, message, 'Введи количество ссылок для регистрации, которое вам нужно')
    await state.set_state(EventState.waiting_links_count)


# --------------------------------------------------------------------------------

@router.message(EventState.waiting_links_count)
async def make_link(message: Message, state: FSMContext):
    """
    Generates and sends registration and confirmation links.

    Args:
        message (Message): The user message.
        state (FSMContext): The state context.

    Returns:
        None
    """
    data = await state.get_data()
    name = data.get('name')
    links = ''
    bot_username = await get_bot_username()

    if not await is_number_in_range(message.text):
        await safe_send_message(bot, message, 'Введи число от 1 до 20')
        return

    for i in range(1, int(message.text) + 1):
        data1 = f'reg_{name}_{i}'
        links += f"https://t.me/{bot_username}?start={data1}\n"
    data2 = name
    url2 = f"https://t.me/{bot_username}?start={data2}"

    await safe_send_message(bot, message, f"все круто, все создано!!\nссылки для регистрации:"
                                          f"\n{links}"
                                          f"\nссылка для подтверждения:"
                                          f"\n{url2}", reply_markup=main_reply_keyboard())
    await state.clear()
