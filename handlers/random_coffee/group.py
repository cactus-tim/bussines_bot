"""
Random Coffee Group Setup

Handlers for configuring Random Coffee settings in group chats.
"""

# --------------------------------------------------------------------------------

from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RandomCoffeeGroupSettings
from handlers.states import GroupSettingsStates
from utils.random_coffee.scheduler import RandomCoffeeScheduler

# --------------------------------------------------------------------------------

router = Router()

# --------------------------------------------------------------------------------

@router.message(Command("setup_coffee"))
async def cmd_setup_coffee(message: Message, state: FSMContext, session: AsyncSession):
    """
    Handle /setup_coffee command in group chats.

    Args:
        message (Message): Incoming message from the group chat.
        state (FSMContext): Finite state machine context.
        session (AsyncSession): SQLAlchemy async session.

    Returns:
        None
    """
    if message.chat.type not in ["group", "supergroup"]:
        await message.answer("Эта команда доступна только в групповых чатах.")
        return

    chat_member = await message.bot.get_chat_member(
        chat_id=message.chat.id,
        user_id=message.from_user.id
    )
    if chat_member.status not in ("administrator", "creator"):
        await message.answer(
            "Только администраторы группы могут настраивать Random Coffee."
        )
        return

    await message.answer(
        "Давайте настроим Random Coffee для вашей группы!\n\n"
        "В какой день недели отправлять напоминание об участии?\n"
        "Напишите день недели (например, 'пятница'):"
    )
    await state.set_state(GroupSettingsStates.waiting_for_reminder_day)

# --------------------------------------------------------------------------------

@router.message(GroupSettingsStates.waiting_for_reminder_day)
async def process_reminder_day(message: Message, state: FSMContext):
    """
    Process input for the reminder day.

    Args:
        message (Message): Incoming message with the day input.
        state (FSMContext): Finite state machine context.

    Returns:
        None
    """
    day = message.text.lower()
    valid_days = [
        "понедельник", "вторник", "среда",
        "четверг", "пятница", "суббота", "воскресенье"
    ]

    if day not in valid_days:
        await message.answer("Пожалуйста, введите корректный день недели:")
        return

    await state.update_data(reminder_day=day)
    await message.answer(
        "В какое время отправлять напоминание?\n"
        "Введите время в формате ЧЧ:ММ (например, '10:00'):"
    )
    await state.set_state(GroupSettingsStates.waiting_for_reminder_time)

# --------------------------------------------------------------------------------

@router.message(GroupSettingsStates.waiting_for_reminder_time)
async def process_reminder_time(message: Message, state: FSMContext):
    """
    Process input for the reminder time.

    Args:
        message (Message): Incoming message with the time input.
        state (FSMContext): Finite state machine context.

    Returns:
        None
    """
    time = message.text
    if not time.count(":") == 1:
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, '10:00'):")
        return

    try:
        hour, minute = map(int, time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное время в формате ЧЧ:ММ:")
        return

    await state.update_data(reminder_time=time)
    await message.answer(
        "В какой день недели составлять пары?\n"
        "Напишите день недели (например, 'понедельник'):"
    )
    await state.set_state(GroupSettingsStates.waiting_for_pairing_day)

# --------------------------------------------------------------------------------

@router.message(GroupSettingsStates.waiting_for_pairing_day)
async def process_pairing_day(message: Message, state: FSMContext):
    """
    Process input for the pairing day.

    Args:
        message (Message): Incoming message with the day input.
        state (FSMContext): Finite state machine context.

    Returns:
        None
    """
    day = message.text.lower()
    valid_days = [
        "понедельник", "вторник", "среда",
        "четверг", "пятница", "суббота", "воскресенье"
    ]

    if day not in valid_days:
        await message.answer("Пожалуйста, введите корректный день недели:")
        return

    await state.update_data(pairing_day=day)
    await message.answer(
        "В какое время составлять пары?\n"
        "Введите время в формате ЧЧ:ММ (например, '10:00'):"
    )
    await state.set_state(GroupSettingsStates.waiting_for_pairing_time)

# --------------------------------------------------------------------------------

@router.message(GroupSettingsStates.waiting_for_pairing_time)
async def process_pairing_time(message: Message, state: FSMContext, session: AsyncSession):
    """
    Process input for the pairing time and save group settings.

    Args:
        message (Message): Incoming message with the time input.
        state (FSMContext): Finite state machine context.
        session (AsyncSession): SQLAlchemy async session.

    Returns:
        None
    """
    time = message.text
    if not time.count(":") == 1:
        await message.answer("Пожалуйста, введите время в формате ЧЧ:ММ (например, '10:00'):")
        return

    try:
        hour, minute = map(int, time.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError
    except ValueError:
        await message.answer("Пожалуйста, введите корректное время в формате ЧЧ:ММ:")
        return

    data = await state.get_data()
    data["pairing_time"] = time

    settings = RandomCoffeeGroupSettings(
        chat_id=message.chat.id,
        reminder_day=data["reminder_day"],
        reminder_time=data["reminder_time"],
        pairing_day=data["pairing_day"],
        pairing_time=data["pairing_time"],
        created_at=datetime.now().isoformat(),
        updated_at=datetime.now().isoformat()
    )
    session.add(settings)
    await session.commit()

    scheduler = RandomCoffeeScheduler(message.bot, session.get_bind())
    await scheduler.setup_group_schedule(
        chat_id=message.chat.id,
        reminder_day=data["reminder_day"],
        reminder_time=data["reminder_time"],
        pairing_day=data["pairing_day"],
        pairing_time=data["pairing_time"]
    )

    await message.answer(
        "Настройки Random Coffee успешно сохранены!\n\n"
        f"Напоминания будут отправляться каждый {data['reminder_day']} в {data['reminder_time']}\n"
        f"Пары будут составляться каждый {data['pairing_day']} в {data['pairing_time']}"
    )
    await state.clear()
