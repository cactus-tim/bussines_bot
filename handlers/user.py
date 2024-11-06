from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.filters.command import CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.error import safe_send_message
from bot_instance import bot
from database.req import get_user, create_user, create_user_x_event_row
from keyboards.keyboards import single_command_button_keyboard


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    hash_value = command.args
    if hash_value:
        user = await get_user(message.from_user.id)
        if user == "not created":
            await create_user(message.from_user.id, {'handler': message.from_user.username})
            name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
            await safe_send_message(bot, message.from_user.id, text=f"{name}, привет от команды HSE SPB Business Club 🎉\n\n"
                                                       "Здесь можно будет принимать участие в розыгрышах, подавать заявку на отбор в команду "
                                                       "и закрытый клуб, а также задавать вопросы и получать анонсы "
                                                       "мероприятий в числе первых.\n\n"
                                                       "Рекомендуем оставить уведомления включенными: так ты не пропустишь ни одно важное "
                                                       "событие клуба.\n\n"
                                                       "Также у нас есть Telegram-канал, где мы регулярно публикуем полезные посты на тему "
                                                       "бизнеса.\n"
                                                       "Подписывайся: @HSE_SPB_Business_Club",
                                    reply_markup=single_command_button_keyboard())
        await create_user_x_event_row(message.from_user.id, hash_value)
        await safe_send_message(bot, message, text="QR-код удачно отсканирован!", reply_markup=single_command_button_keyboard())
    else:
        await create_user(message.from_user.id, {'handler': message.from_user.username})
        name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
        await safe_send_message(bot, message, text=f"{name}, привет от команды HSE SPB Business Club 🎉\n\n"
                                "Здесь можно будет принимать участие в розыгрышах, подавать заявку на отбор в команду "
                                                   "и закрытый клуб, а также задавать вопросы и получать анонсы "
                                                   "мероприятий в числе первых.\n\n"
                                "Рекомендуем оставить уведомления включенными: так ты не пропустишь ни одно важное "
                                                   "событие клуба.\n\n"
                                "Также у нас есть Telegram-канал, где мы регулярно публикуем полезные посты на тему "
                                                   "бизнеса.\n"
                                "Подписывайся: @HSE_SPB_Business_Club",
                                reply_markup=single_command_button_keyboard())


@router.message(Command("info"))
async def cmd_info(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(bot, message, text="Список доступных команд:\n"
                                                   "/start - перезапуск бота\n"
                                                   "/info - информация о доступных комнадах\n"
                                                   "/quest - пройти анкетирование для отбора в команду\n"
                                                   "/send_stat - получить статистику о пользователях\n"
                                                   "/send_post - отправить пост пользователям\n"
                                                   "/add_event - в разработке\n"
                                                   "/end_event - завершить событие\n")
    else:
        await safe_send_message(bot, message, text="Список доступных команд:\n"
                                                   "/start - перезапуск бота\n"
                                                   "/info - информация о доступных комнадах\n"
                                                   "/quest - пройти анкетирование для отбора в команду\n",
                                reply_markup=single_command_button_keyboard())
