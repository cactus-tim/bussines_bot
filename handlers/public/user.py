from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from config.texts.commands import INFO_ADMIN, INFO_USER
from database.req import get_user, get_all_user_events, get_user_rank_by_money, \
    get_top_10_users_by_money, get_event
from handlers.error import safe_send_message
from handlers.utils.base import get_bot_username
from keyboards.keyboards import single_command_button_keyboard, events_ikb, top_ikb

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)


@router.message(Command("info"))
async def cmd_info(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(bot, message, text=INFO_ADMIN,
                                reply_markup=single_command_button_keyboard())
    else:
        await safe_send_message(bot, message, text=INFO_USER)


@router.message(Command('profile'))
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    rank = await get_user_rank_by_money(message.from_user.id)
    msg = f'👤 <b>Личный кабинет {name}</b>\n\n' \
          f'🎯 <b>Статистика:</b>\n' \
          f'• Посещено мероприятий: {user.event_cnt}\n' \
          f'• Текущая серия: {user.strick}\n' \
          f'• Рефералов: {user.ref_cnt}\n' \
          f'• Монеток: {user.money}\n' \
          f'• Место в топе: {rank}'
    await safe_send_message(bot, message, msg, reply_markup=top_ikb())


@router.callback_query(F.data == 'top')
async def top_inline(message: Message):
    await cmd_top(message)


@router.message(Command('top'))
async def cmd_top(message: Message):
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


@router.message(Command("get_ref"))
async def get_ref_v2_part1(message: Message):
    events = await get_all_user_events(message.from_user.id)
    if not events:
        await safe_send_message(bot, message, "Вы не зарегистрированы ни на одно событие и не можете никого никуда "
                                              "пригласить", reply_markup=single_command_button_keyboard())
        return
    await safe_send_message(bot, message, "Выберете событие, на которое хотите пригласить друга",
                            reply_markup=events_ikb(events))


@router.callback_query(lambda c: not c.data.startswith(("qr_", "event_", "hse_", "verify_", "another_", "post_", "stat_", "link_", "unreg_", "cancel", "confirm", "reroll", "top")))
async def get_ref_v2_part2(callback: CallbackQuery):
    """Handle event selection for referral link generation."""
    try:
        event = await get_event(callback.data)
        if event == "not created":
            await callback.answer("Мероприятие не найдено")
            return

        data = f'ref_{callback.data}__{callback.from_user.id}'
        bot_username = await get_bot_username()
        url = f"https://t.me/{bot_username}?start={data}"

        await safe_send_message(bot, callback,
                                f"Вот твоя реферальная ссылка для событие {event.desc}:\n{url}",
                                reply_markup=single_command_button_keyboard()
                                )
    except Exception as e:
        print(f"Referral link generation error: {e}")
        await callback.answer("Произошла ошибка при создании реферальной ссылки")
