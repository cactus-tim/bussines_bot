"""
User commands and profile
Handles info, profile, top and referral link generation.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from database.req import get_all_user_events, get_event
from handlers.error import safe_send_message
from handlers.utils.base import get_bot_username
from keyboards import main_reply_keyboard, events_ikb

# --------------------------------------------------------------------------------

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# --------------------------------------------------------------------------------

@router.message(Command("get_ref"))
async def get_ref_v2_part1(message: Message):
    """
    Start referral link generation for user.

    Args:
        message (Message): Incoming user message.

    Returns:
        None
    """
    events = await get_all_user_events(message.from_user.id)
    if not events:
        await safe_send_message(
            bot, message,
            "Вы не зарегистрированы ни на одно событие и не можете никого никуда пригласить",
            reply_markup=main_reply_keyboard()
        )
        return

    await safe_send_message(
        bot, message,
        "Выберете событие, на которое хотите пригласить друга",
        reply_markup=events_ikb(events)
    )


@router.callback_query(lambda c: not c.data.startswith((
        "qr_", "event_", "hse_", "verify_", "another_", "post_", "stat_",
        "link_", "unreg_", "cancel", "confirm", "reroll", "top", "quest_", "face_"
)))
async def get_ref_v2_part2(callback: CallbackQuery):
    """
    Handle event selection for referral link generation.

    Args:
        callback (CallbackQuery): Callback query from Telegram.

    Returns:
        None
    """
    try:
        event = await get_event(callback.data)
        if event == "not created":
            await callback.answer("Мероприятие не найдено")
            return

        data = f'ref_{callback.data}__{callback.from_user.id}'
        bot_username = await get_bot_username()
        url = f"https://t.me/{bot_username}?start={data}"

        await safe_send_message(
            bot, callback,
            f"Вот твоя реферальная ссылка для событие {event.desc}:\n{url}",
            reply_markup=main_reply_keyboard()
        )
    except Exception as e:
        print(f"Referral link generation error: {e}")
        await callback.answer("Произошла ошибка при создании реферальной ссылки")
