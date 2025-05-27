"""
User commands and profile
Handles info, profile, top and referral link generation.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from config.texts.commands import INFO_ADMIN, INFO_USER
from database.req import (
    get_user, get_all_user_events, get_user_rank_by_money,
    get_top_10_users_by_money, get_event
)
from handlers.error import safe_send_message
from handlers.utils.base import get_bot_username
from keyboards.keyboards import single_command_button_keyboard, events_ikb, top_ikb

# --------------------------------------------------------------------------------

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# --------------------------------------------------------------------------------


@router.message(Command("info"))
async def cmd_info(message: Message):
    """
    Show help info for user or admin.

    Args:
        message (Message): Incoming user message.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(
            bot, message,
            text=INFO_ADMIN,
            reply_markup=single_command_button_keyboard()
        )
    else:
        await safe_send_message(bot, message, text=INFO_USER)


@router.message(Command('profile'))
async def cmd_profile(message: Message):
    """
    Display user's personal profile and stats.

    Args:
        message (Message): Incoming user message.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    name = message.from_user.first_name or message.from_user.username
    rank = await get_user_rank_by_money(message.from_user.id)
    msg = (
        f'👤 <b>Личный кабинет {name}</b>\n\n'
        f'🎯 <b>Статистика:</b>\n'
        f'• Посещено мероприятий: {user.event_cnt}\n'
        f'• Рефералов: {user.ref_cnt}\n'
        f'• Монеток: {user.money}\n'
        f'• Место в топе: {rank}'
    )
    await safe_send_message(bot, message, msg, reply_markup=top_ikb())


# --------------------------------------------------------------------------------


@router.callback_query(F.data == 'top')
async def top_inline(message: Message):
    """
    Handle inline top leaderboard request.

    Args:
        message (Message): Callback query object.

    Returns:
        None
    """
    await cmd_top(message)


@router.message(Command('top'))
async def cmd_top(message: Message):
    """
    Display the top-10 users leaderboard.

    Args:
        message (Message): Incoming user message.

    Returns:
        None
    """
    top = await get_top_10_users_by_money()
    msg = ''
    flag = True
    for i in range(len(top)):
        if top[i].id == message.from_user.id:
            flag = False
            msg += f'{i + 1}. Вы - {top[i].money}\n'
        else:
            msg += f'{i + 1}. {top[i].handler} - {top[i].money}\n'

    if flag:
        rank = await get_user_rank_by_money(message.from_user.id)
        user = await get_user(message.from_user.id)
        msg += f"\n{rank}. Вы - {user.money}"

    await safe_send_message(bot, message, msg)
