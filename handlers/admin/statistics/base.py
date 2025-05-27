"""
Statistics Handlers

Handlers for sending various types of statistics to superusers.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from database.req import get_user, get_all_events
from handlers.admin.statistics.utils import (
    get_stat_all,
    get_stat_all_in_ev,
    get_stat_quest,
    get_stat_ad_give_away,
    get_stat_reg_out,
    get_stat_reg,
)
from handlers.error import safe_send_message
from handlers.states import StatState
from keyboards.keyboards import post_ev_target, stat_target, single_command_button_keyboard

# --------------------------------------------------------------------------------

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)

# --------------------------------------------------------------------------------

@router.message(Command("send_stat"))
async def cmd_send_stat(message: Message):
    """
    Send the initial statistics selection menu to the superuser.

    Args:
        message (Message): Incoming message from the user.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(
        bot,
        message,
        text="Выберете какую статистику вы хотите получить",
        reply_markup=stat_target(),
    )

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "stat_all")
async def cmd_stat_all(callback: CallbackQuery):
    """
    Send overall statistics to the user.

    Args:
        callback (CallbackQuery): Incoming callback from button press.

    Returns:
        None
    """
    await get_stat_all(callback.from_user.id)

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "stat_ev")
async def cmd_stat_ev(callback: CallbackQuery, state: FSMContext):
    """
    Start process for event-specific statistics.

    Args:
        callback (CallbackQuery): Incoming callback from button press.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий",
                                reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:",
                            reply_markup=post_ev_target(events))
    await state.set_state(StatState.waiting_for_ev)

# --------------------------------------------------------------------------------

@router.message(StatState.waiting_for_ev)
async def process_post_to_all(message: Message, state: FSMContext):
    """
    Handle event selection for statistics.

    Args:
        message (Message): Incoming message with event name.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    await get_stat_all_in_ev(message.from_user.id, message.text)
    await state.clear()

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "stat_quest")
async def cmd_stat_ev(callback: CallbackQuery):
    """
    Send statistics on questions.

    Args:
        callback (CallbackQuery): Incoming callback from button press.

    Returns:
        None
    """
    await get_stat_quest(callback.from_user.id)

# --------------------------------------------------------------------------------

@router.callback_query(F.data == 'stat_give_away')
async def cmd_stat_give_away(callback: CallbackQuery, state: FSMContext):
    """
    Start additional giveaway statistics process.

    Args:
        callback (CallbackQuery): Incoming callback from button press.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий",
                                reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:",
                            reply_markup=post_ev_target(events))
    await state.set_state(StatState.waiting_for_give_away_ev)

# --------------------------------------------------------------------------------

@router.message(StatState.waiting_for_give_away_ev)
async def cmd_stat_give_away2(message: Message, state: FSMContext):
    """
    Handle event name for giveaway statistics.

    Args:
        message (Message): Message containing event name or 'quit'.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await state.clear()
        return
    await state.update_data({'event_name': message.text})
    await safe_send_message(
        bot,
        message,
        'Введите юзер id организатора дополнительного розыгрыша\n\nДля отмены введите quit',
    )
    await state.set_state(StatState.waiting_user_id)

# --------------------------------------------------------------------------------

@router.message(StatState.waiting_user_id)
async def cmd_stat_give_away3(message: Message, state: FSMContext):
    """
    Handle organizer ID for giveaway statistics.

    Args:
        message (Message): Message containing user ID or 'quit'.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await state.clear()
        return
    data = await state.get_data()
    event_name = data.get('event_name')
    await get_stat_ad_give_away(message.from_user.id, int(message.text), event_name)
    await state.clear()

# --------------------------------------------------------------------------------

@router.callback_query(F.data == 'stat_reg_out')
async def cmd_stat_reg(callback: CallbackQuery, state: FSMContext):
    """
    Start process for registration outflow statistics.

    Args:
        callback (CallbackQuery): Incoming callback from button press.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий",
                                reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:",
                            reply_markup=post_ev_target(events))
    await state.set_state(StatState.waiting_for_ev1)

# --------------------------------------------------------------------------------

@router.message(StatState.waiting_for_ev1)
async def cmd_stat_reg2(message: Message, state: FSMContext):
    """
    Handle event name for registration outflow statistics.

    Args:
        message (Message): Message with event name.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    await get_stat_reg_out(message.from_user.id, message.text)
    await state.clear()

# --------------------------------------------------------------------------------

@router.callback_query(F.data == 'stat_reg')
async def cmd_stat_reg(callback: CallbackQuery, state: FSMContext):
    """
    Start process for registration statistics.

    Args:
        callback (CallbackQuery): Incoming callback from button press.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий",
                                reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:",
                            reply_markup=post_ev_target(events))
    await state.set_state(StatState.waiting_for_ev2)

# --------------------------------------------------------------------------------

@router.message(StatState.waiting_for_ev2)
async def cmd_stat_reg2(message: Message, state: FSMContext):
    """
    Handle event name for registration statistics.

    Args:
        message (Message): Message with event name.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    await get_stat_reg(message.from_user.id, message.text)
    await state.clear()
