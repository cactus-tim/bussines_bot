import base64

import requests
from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.filters.command import CommandObject
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import urllib.parse

from handlers.error import safe_send_message, make_short_link
from bot_instance import bot
from database.req import get_user, create_user, create_user_x_event_row, update_user, get_all_user_events, get_event, \
    update_user_x_event_row_status
from keyboards.keyboards import single_command_button_keyboard, events_ikb
from handlers.quest import start

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    hash_value = command.args
    user = await get_user(message.from_user.id)
    if hash_value:
        if hash_value[:3] == 'reg':
            if user == "not created":
                await create_user(message.from_user.id,
                                  {'handler': message.from_user.username, 'first_contact': hash_value[4:]})
                name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
                await safe_send_message(bot, message.from_user.id,
                                        text=f"{name}, привет от команды HSE SPB Business Club 🎉\n\n"
                                             "Здесь можно будет принимать участие в розыгрышах, подавать заявку на "
                                             "отбор в команду"
                                             "и закрытый клуб, а также задавать вопросы и получать анонсы "
                                             "мероприятий в числе первых.\n\n"
                                             "Рекомендуем оставить уведомления включенными: так ты не пропустишь ни "
                                             "одно важное"
                                             "событие клуба.\n\n"
                                             "Также у нас есть Telegram-канал, где мы регулярно публикуем полезные "
                                             "посты на тему"
                                             "бизнеса.\n"
                                             "Подписывайся: @HSE_SPB_Business_Club",
                                        reply_markup=single_command_button_keyboard())
            await create_user_x_event_row(message.from_user.id, hash_value[4:])
            await safe_send_message(bot, message, text="Вы удачно зарегистрировались!",
                                    reply_markup=single_command_button_keyboard())
        elif hash_value[:3] == 'ref':
            if hash_value[3] == '_':
                event_part, user_id = hash_value.split("__")
                event_name = event_part.replace("ref_", "")
                user_id = int(user_id)
                if user == "not created":
                    await create_user(message.from_user.id,
                                      {'handler': message.from_user.username, 'first_contact': event_name})
                    # TODO: give reward to both
                    await safe_send_message(bot, user_id, f"По твоей рефеальной сслыке зарегистрировался "
                                                          f"пользователь @{message.from_user.username}!")

                await safe_send_message(bot, user_id, f"По твоей рефеальной сслыке зарегистрировался на событие"
                                                      f" пользователь @{message.from_user.username}!")
                # TODO: give reward to both (ref_v2)
                # TODO: some messages, discuss wth Anton/Vitaly
                await create_user_x_event_row(message.from_user.id, event_name)
            else:
                if user == "not created":
                    await create_user(message.from_user.id,
                                      {'handler': message.from_user.username, 'first_contact': hash_value[3:]})
                    # TODO: give reward to both
                    await safe_send_message(bot, int(hash_value[3:]), f"По твоей рефеальной сслыке зарегистрировался "
                                                                      f"пользователь @{message.from_user.username}!")
                name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
                await safe_send_message(bot, message, text=f"{name}, привет от команды HSE SPB Business Club 🎉\n\n"
                                                           "Здесь можно будет принимать участие в розыгрышах, подавать "
                                                           "заявку на отбор в команду"
                                                           "и закрытый клуб, а также задавать вопросы и получать анонсы "
                                                           "мероприятий в числе первых.\n\n"
                                                           "Рекомендуем оставить уведомления включенными: так ты не "
                                                           "пропустишь ни одно важное"
                                                           "событие клуба.\n\n"
                                                           "Также у нас есть Telegram-канал, где мы регулярно публикуем "
                                                           "полезные посты на тему"
                                                           "бизнеса.\n"
                                                           "Подписывайся: @HSE_SPB_Business_Club",
                                        reply_markup=single_command_button_keyboard())
        elif hash_value == 'otbor':
            if user == "not created":
                await create_user(message.from_user.id,
                                  {'handler': message.from_user.username, 'first_contact': hash_value})
            name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
            await safe_send_message(bot, message, f'Привет, {name}!', reply_markup=single_command_button_keyboard())
            await start(message)
        else:
            if user == "not created":
                await create_user(message.from_user.id,
                                  {'handler': message.from_user.username, 'first_contact': hash_value})
                name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
                await safe_send_message(bot, message.from_user.id,
                                        text=f"{name}, привет от команды HSE SPB Business Club 🎉\n\n"
                                             "Здесь можно будет принимать участие в розыгрышах, подавать заявку на "
                                             "отбор в команду"
                                             "и закрытый клуб, а также задавать вопросы и получать анонсы "
                                             "мероприятий в числе первых.\n\n"
                                             "Рекомендуем оставить уведомления включенными: так ты не пропустишь ни "
                                             "одно важное"
                                             "событие клуба.\n\n"
                                             "Также у нас есть Telegram-канал, где мы регулярно публикуем полезные "
                                             "посты на тему"
                                             "бизнеса.\n"
                                             "Подписывайся: @HSE_SPB_Business_Club",
                                        reply_markup=single_command_button_keyboard())
            tr = await update_user_x_event_row_status(message.from_user.id, hash_value, 'been')
            if not tr:
                await create_user_x_event_row(message.from_user.id, hash_value)
                await update_user_x_event_row_status(message.from_user.id, hash_value, 'been')
            await safe_send_message(bot, message, text="QR-код удачно отсканирован!",
                                    reply_markup=single_command_button_keyboard())
    else:
        if user == "not created":
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
                                                   "/get_ref - получить реферальную ссылку\n"
                                                   "/get_ref_to_event - получить реферальную ссылку на событие\n"
                                                   "/send_stat - получить статистику о пользователях\n"
                                                   "/send_post - отправить пост пользователям\n"
                                                   "/add_event - создает новое событие\n"
                                                   "/end_event - завершить событие\n"
                                                   "/get_link - получить ссылки на событие\n",
                                reply_markup=single_command_button_keyboard())
    else:
        await safe_send_message(bot, message, text="Список доступных команд:\n"
                                                   "/start - перезапуск бота\n"
                                                   "/info - информация о доступных комнадах\n"
                                                   "/quest - пройти анкетирование для отбора в команду\n"
                                                   "/get_ref - получить реферальную ссылку\n"
                                                   "/get_ref_to_event - получить реферальную ссылку на событие\n",
                                reply_markup=single_command_button_keyboard())


@router.message(Command("get_ref"))
async def get_ref(message: Message):
    data = f'ref{message.from_user.id}'
    url = f"https://t.me/HSE_SPB_Business_Club_Bot?start={data}"
    short_url = await make_short_link(url)
    if short_url:
        await safe_send_message(bot, message, "Вот твоя реферальная ссылка:\n"
                                              f"{short_url}", reply_markup=single_command_button_keyboard()
                                )
    else:
        await safe_send_message(bot, message, "Какая то ошибка. Попробуйте еще раз позже", reply_markup=single_command_button_keyboard())


@router.message(Command("get_ref_to_event"))
async def get_ref_v2_part1(message: Message):
    events = await get_all_user_events(message.from_user.id)
    if not events:
        await safe_send_message(bot, message, "Вы не зарегестрированны ни на одно событие и не можете никого никуда "
                                              "пригласить", reply_markup=single_command_button_keyboard())
        return
    await safe_send_message(bot, message, "Выберети событие, на которое хотите пригласить друга",
                            reply_markup=events_ikb(events))


@router.callback_query()
async def get_ref_v2_part2(callback: CallbackQuery):
    event = await get_event(callback.data)
    data = f'ref_{event.name}__{callback.from_user.id}'
    url = f"https://t.me/HSE_SPB_Business_Club_Bot?start={data}"
    short_url = await make_short_link(url)
    if short_url:
        await safe_send_message(bot, callback, f"Вот твоя реферальная ссылка для событие {event.desc}:\n"
                                               f"{short_url}", reply_markup=single_command_button_keyboard()
                                )
    else:
        await safe_send_message(bot, callback, "Какая то ошибка. Попробуйте еще раз позже", reply_markup=single_command_button_keyboard())
