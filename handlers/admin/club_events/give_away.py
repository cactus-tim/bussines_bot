"""
Giveaway and Networking
Handlers for creating giveaways and assigning themes in networking club_events.
"""

# --------------------------------------------------------------------------------

import random

from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.settings import TOKEN
from config.texts.admin import THEMES
from database.req import (
    get_user, get_all_events, create_host,
    get_all_for_networking, delete_all_from_networking
)
from handlers.error import safe_send_message
from handlers.states import GiveAwayState
from keyboards import (
    post_ev_target, main_reply_keyboard, get_ref_ikb
)
from utils.validators import is_number_in_range

# --------------------------------------------------------------------------------

router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# --------------------------------------------------------------------------------

@router.message(Command('create_give_away'))
async def cmd_create_give_away(message: Message, state: FSMContext):
    """
    Start giveaway creation process by selecting an event.

    Args:
        message (Message): Incoming command message.
        state (FSMContext): FSM state context.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return

    events = await get_all_events()
    if not events:
        await safe_send_message(
            bot, message,
            text="У вас нет событий",
            reply_markup=main_reply_keyboard()
        )
        await state.clear()
        return

    await safe_send_message(
        bot, message,
        text="Выберете событие:",
        reply_markup=post_ev_target(events)
    )
    await state.set_state(GiveAwayState.waiting_event)


# --------------------------------------------------------------------------------

@router.message(GiveAwayState.waiting_event)
async def cmd_create_give_away2(message: Message, state: FSMContext):
    """
    Ask for organization name after event is selected.

    Args:
        message (Message): User message with event name.
        state (FSMContext): FSM state context.

    Returns:
        None
    """
    await state.update_data({'event_name': message.text})
    await safe_send_message(
        bot, message,
        'Введите название организации\n\nДля отмены введите quit'
    )
    await state.set_state(GiveAwayState.waiting_org_name)


# --------------------------------------------------------------------------------

@router.message(GiveAwayState.waiting_org_name)
async def cmd_create_give_away3(message: Message, state: FSMContext):
    """
    Ask for host ID after organization name.

    Args:
        message (Message): User message with organization name.
        state (FSMContext): FSM state context.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await state.clear()
        return

    await state.update_data({'org_name': message.text})
    await safe_send_message(
        bot, message,
        'Введите айди организатора\n\nЕсли хотите использовать свое айди = отправьте Я'
        '\n\nДля отмены введите quit'
    )
    await state.set_state(GiveAwayState.waiting_id)


# --------------------------------------------------------------------------------

@router.message(GiveAwayState.waiting_id)
async def cmd_create_give_away4(message: Message, state: FSMContext):
    """
    Finalize giveaway by creating the host.

    Args:
        message (Message): User message with ID or "я".
        state (FSMContext): FSM state context.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await state.clear()
        return

    data = await state.get_data()
    event_name = data.get('event_name')
    org_name = data.get('org_name')
    user_id = message.from_user.id if message.text.lower() == 'я' else message.text

    if not await is_number_in_range(user_id):
        await safe_send_message(bot, message, 'Введи число - айди')
        return

    user_id = int(user_id)
    await create_host(user_id, event_name, org_name)

    await safe_send_message(
        bot, message,
        'Готово!',
        reply_markup=get_ref_ikb(event_name)
    )
    await state.clear()


# --------------------------------------------------------------------------------

@router.message(Command("give_colors"))
async def give_colors(message: Message):
    """
    Assign random themes to networking participants.

    Args:
        message (Message): Incoming command message.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return

    users = await get_all_for_networking()
    if not users:
        await safe_send_message(
            bot, message.from_user.id,
            "Пока никто не зарегистрировался на нетворкинг"
        )
        return

    for user in users:
        color = random.choice(THEMES)
        await safe_send_message(bot, user, f"Ваша тема - {color}!")

    await delete_all_from_networking()
    await safe_send_message(bot, message.from_user.id, "Готово")
