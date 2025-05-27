"""
Start command handler
Handles /start command and hash-based user scenarios.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.settings import TOKEN
from config.texts.commands import WELCOME_MESSAGE
from handlers.error import safe_send_message
from handlers.public.quest import start
from handlers.public.utils.base import create_user_if_not_exists
from keyboards.keyboards import (
    single_command_button_keyboard
)
from .club_events.qr import cmd_check_qr
from .club_events.registration import handle_networking_hash, handle_reg_hash, handle_ref_hash, \
    handle_default_hash

# --------------------------------------------------------------------------------

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# --------------------------------------------------------------------------------


async def send_welcome_message(user_id: int, username: str, message: Message):
    """
    Send a personalized welcome message.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        message (Message): Incoming message object.

    Returns:
        None
    """
    name = message.from_user.first_name if message.from_user.first_name else username
    await safe_send_message(
        bot, message,
        text=WELCOME_MESSAGE.format(name=name),
        reply_markup=single_command_button_keyboard()
    )


async def handle_otbor_hash(user_id: int, username: str, message: Message):
    """
    Handle 'otbor' hash.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        message (Message): Incoming message object.

    Returns:
        None
    """
    await create_user_if_not_exists(user_id, username, 'otbor')
    name = message.from_user.first_name if message.from_user.first_name else username
    await safe_send_message(bot, message, f'Привет, {name}!', reply_markup=single_command_button_keyboard())
    await start(message)


# --------------------------------------------------------------------------------


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    """
    Handle the /start command and route user by hash.

    Args:
        message (Message): Incoming message object.
        command (CommandObject): Parsed command data.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    hash_value = command.args
    user_id = message.from_user.id
    username = message.from_user.username

    await create_user_if_not_exists(user_id, username, hash_value)

    if hash_value and hash_value.startswith('qr_'):
        check_qr_command = CommandObject(command=message.text, args=hash_value)
        await cmd_check_qr(message, check_qr_command)
        return

    if hash_value:
        if hash_value == 'networking':
            await handle_networking_hash(user_id, username, message)
        elif hash_value[:3] == 'reg':
            await handle_reg_hash(user_id, username, hash_value, message, state)
        elif hash_value[:3] == 'ref':
            await handle_ref_hash(user_id, username, hash_value, message, state)
        elif hash_value == 'otbor':
            await handle_otbor_hash(user_id, username, message)
        else:
            await handle_default_hash(user_id, username, hash_value, message)
    else:
        await create_user_if_not_exists(user_id, username)
        await send_welcome_message(user_id, username, message)

    await safe_send_message(
        bot, message,
        'Используйте /info чтобы получить информацию о доступных командах'
    )
