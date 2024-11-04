from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardRemove

from error import safe_send_message
from bot_instance import bot
from database.req import get_user, create_user


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await create_user(message.from_user.id, {'handler': message.from_user.username})
    await safe_send_message(bot, message, text="Какое то приветственное сообщение")


@router.message(Command("info"))
async def cmd_info(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(bot, message, text="Список доступных команд:"
                                                   "\\start - перезапуск бота"
                                                   "\\info - информация о доступных комнадах"
                                                   "\\quest - пройти анкетирование для отбора в команду"
                                                   "\\send_stat"
                                                   "\\send_post"
                                                   "\\add_vacancy"
                                                   "\\dell_vacancy"
                                                   "\\add_event"
                                                   "\\end_event")
    else:
        await safe_send_message(bot, message, text="Список доступных команд:"
                                                   "\\start - перезапуск бота"
                                                   "\\info - информация о доступных комнадах"
                                                   "\\quest - пройти анкетирование для отбора в команду")
