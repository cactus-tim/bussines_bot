import base64
from aiogram.utils.deep_linking import create_start_link, decode_payload
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
    update_user_x_event_row_status, update_reg_event, check_completly_reg_event, create_reg_event, get_reg_event, \
    get_user_x_event_row, get_ref_give_away, create_ref_give_away
from keyboards.keyboards import single_command_button_keyboard, events_ikb, yes_no_ikb, yes_no_hse_ikb
from handlers.quest import start

router = Router()


class EventReg(StatesGroup):
    waiting_name = State()
    waiting_surname = State()
    waiting_fathername = State()
    waiting_mail = State()
    waiting_phone = State()
    waiting_org = State()


give_away_ids = [1568674379, 1426453089, 483458201]


mmsg = """
🥞 Встреча с совладельцем «Теремка» в НИУ ВШЭ

📎 Программа выступления:

• Как с нуля построить компанию с многомиллиардным оборотом?
• Почему клиенты возвращаются в «Теремок» снова и снова?
• Какие навыки помогли выстроить успешную организацию в высоко конкурентной среде?
• Как сделать компанию успешной через закладываемые ценности? 

📅 4 декабря в 18:00

📍 НИУ ВШЭ, Кантемировская улица, 3к1, ауд. 436

Вся дальнейшая информация будет в нашем канале @HSE_SPB_Business_Club
"""


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    hash_value = command.args  # TODO: after 04_12 event hash_value = decode_payload(command.args)
    user = await get_user(message.from_user.id)
    if hash_value:
        if hash_value[:3] == 'reg':
            if user == "not created":
                await create_user(message.from_user.id,
                                  {'handler': message.from_user.username, 'first_contact': hash_value[4:]})
            await safe_send_message(bot, message.from_user.id,
                                    text=mmsg,
                                    reply_markup=single_command_button_keyboard())
            event_name = hash_value.split('_')[1] + '_' + hash_value.split('_')[2] + '_' + hash_value.split('_')[3]
            user_x_event = await get_user_x_event_row(message.from_user.id, event_name)
            if user_x_event == 'not created':
                await create_user_x_event_row(message.from_user.id, event_name, hash_value.split('_')[-1])
                event = await get_event(event_name)
                if event == 'not created':
                    await safe_send_message(bot, message, 'Такого события не существует..')
                await state.update_data({'name': event_name})
                await safe_send_message(bot, message, f'Хотите зарегистрироваться на мероприятие {event.desc},'
                                                      f'которое пройдет {event.date} в {event.time}', reply_markup=yes_no_ikb())
            else:
                await safe_send_message(bot, message, 'Вы уже зарегистрировались на это мероприятие')
        elif hash_value[:3] == 'ref':
            if hash_value[3] == '_':
                event_part, user_id = hash_value.split("__")
                event_name = event_part.replace("ref_", "")
                user_id = int(user_id)
                if user == "not created":
                    await create_user(message.from_user.id,
                                      {'handler': message.from_user.username, 'first_contact': str(user_id)})
                await safe_send_message(bot, message.from_user.id,
                                        text=mmsg,
                                        reply_markup=single_command_button_keyboard())
                if user_id in give_away_ids:
                    ref_give_away = await get_ref_give_away(message.from_user.id, event_name)
                    if not ref_give_away:
                        await create_ref_give_away(message.from_user.id, event_name, user_id)
                        host = await get_user(user_id)
                        await safe_send_message(bot, message, f'Поздравляю, вы учавствуете в розыгрыше, предназначенным только для подписчиков @{host.handler}')
                    else:
                        await safe_send_message(bot, message, 'Вы уже учавствуете в чьем то розыгрыше')
                await safe_send_message(bot, user_id, f"По твоей рефеальной сслыке зарегистрировался на событие"
                                                      f" пользователь @{message.from_user.username}!")
                # TODO: give reward to both (ref_v2)
                user_x_event = await get_user_x_event_row(message.from_user.id, event_name)
                if user_x_event == 'not created':
                    await create_user_x_event_row(message.from_user.id, event_name, str(user_id))
                    event = await get_event(event_name)
                    if event == 'not created':
                        await safe_send_message(bot, message, 'Такого события не существует..')
                    await state.update_data({'name': event_name})
                    await safe_send_message(bot, message, f'Хотите зарегистрироваться на мероприятие {event.desc},'
                                                          f'которое пройдет {event.date} в {event.time}',
                                            reply_markup=yes_no_ikb())
                else:
                    await safe_send_message(bot, message, 'Вы уже зарегистрировались на это мероприятие')
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
                await create_user_x_event_row(message.from_user.id, hash_value, '0')
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


@router.callback_query(F.data == "event_no")
async def reg_event_part0_5(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, "Это очень грустно((", reply_markup=single_command_button_keyboard())
    await state.clear()


@router.callback_query(F.data == "event_yes")
async def reg_event_part1(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, "Вы студент/сотрудник НИУ ВШЭ?", reply_markup=yes_no_hse_ikb())


@router.callback_query(F.data == "hse_yes")
async def reg_event_part1_5(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    event = await get_event(name)
    await safe_send_message(bot, callback, f"Мы вас ждем на мероприятии {event.desc}, которое пройдет {event.date} в {event.time}\n"
                                               f"Место проведение - {event.place}\n\n", reply_markup=single_command_button_keyboard())
    await state.clear()


@router.callback_query(F.data == "hse_no")
async def reg_event_part2(callback: CallbackQuery, state: FSMContext):
    reg_event = await get_reg_event(callback.from_user.id)
    if not reg_event:
        await create_reg_event(callback.from_user.id)
        flag = False
    else:
        flag = await check_completly_reg_event(callback.from_user.id)
    if flag:
        data = await state.get_data()
        name = data.get('name')
        event = await get_event(name)
        await safe_send_message(bot, callback, "Ваши данные уже сохранены!\n"
                                               f"Мы вас ждем на мероприятии {event.desc}, которое пройдет {event.date} в {event.time}\n"
                                               f"Место проведение - {event.place}\n\n"
                                               f"⚠ Обязательно возьмите с собой паспорт!", reply_markup=single_command_button_keyboard())
        await state.clear()
    else:
        await safe_send_message(bot, callback, "Для пропуска на мероприятие нужно будет сообщить ваши данные. Напишите, пожалуйста, ваше имя")
        await state.set_state(EventReg.waiting_name)


@router.message(EventReg.waiting_name)
async def reg_event_part3(message: Message, state: FSMContext):
    await update_reg_event(message.from_user.id, {'name': message.text})
    await safe_send_message(bot, message, 'Напишите, пожалуйста, вашу фамилию')
    await state.set_state(EventReg.waiting_surname)


@router.message(EventReg.waiting_surname)
async def reg_event_part3(message: Message, state: FSMContext):
    await update_reg_event(message.from_user.id, {'surname': message.text})
    await safe_send_message(bot, message, 'Напишите, пожалуйста, ваше отчество')
    await state.set_state(EventReg.waiting_fathername)


@router.message(EventReg.waiting_fathername)
async def reg_event_part3(message: Message, state: FSMContext):
    await update_reg_event(message.from_user.id, {'fathername': message.text})
    await safe_send_message(bot, message, 'Укажите, пожалуйста, ваш мобильный телефон')
    await state.set_state(EventReg.waiting_phone)


@router.message(EventReg.waiting_phone)
async def reg_event_part3(message: Message, state: FSMContext):
    await update_reg_event(message.from_user.id, {'phone': message.text})
    await safe_send_message(bot, message, 'Укажите, пожалуйста, вашу почту')
    await state.set_state(EventReg.waiting_mail)


@router.message(EventReg.waiting_mail)
async def reg_event_part3(message: Message, state: FSMContext):
    await update_reg_event(message.from_user.id, {'mail': message.text})
    await safe_send_message(bot, message, 'Укажите, пожалуйста, из какого вы вуза/организации')
    await state.set_state(EventReg.waiting_org)


@router.message(EventReg.waiting_org)
async def reg_event_part3(message: Message, state: FSMContext):
    await update_reg_event(message.from_user.id, {'org': message.text})
    if await check_completly_reg_event(message.from_user.id):
        data = await state.get_data()
        name = data.get('name')
        event = await get_event(name)
        await safe_send_message(bot, message, f"Мы вас ждем на мероприятии {event.desc}, которое пройдет {event.date} в {event.time}\n"
                                               f"Место проведение - {event.place}\n\n"
                                               f"⚠ Обязательно возьмите с собой паспорт!",
                                reply_markup=single_command_button_keyboard())
    else:
        await safe_send_message(bot, message, 'Что то пошло не так, начните регистрацию заново, пожалуйста\n'
                                              'Для этого повтороно перейдите по ссылке')
    await state.clear()


@router.message(Command("info"))
async def cmd_info(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(bot, message, text="Список доступных команд:\n"
                                                   "/start - перезапуск бота\n"
                                                   "/info - информация о доступных комнадах\n"
                                                   "/quest - пройти анкетирование для отбора в команду\n"
                                                   "/get_ref - получить реферальную ссылку на событие\n"
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
                                                   "/get_ref - получить реферальную ссылку на событие\n",
                                reply_markup=single_command_button_keyboard())


@router.message(Command("get_ref"))
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
    url = f"https://t.me/HSE_SPB_Business_Club_Bot?start={data}"  # TODO: after 04_12 event url = await create_start_link(bot, data, encode=True)
    # short_url = await make_short_link(url)
    # if short_url:
    await safe_send_message(bot, callback, f"Вот твоя реферальная ссылка для событие {event.desc}:\n"
                                           f"{url}", reply_markup=single_command_button_keyboard()
                            )
    # else:
    #     await safe_send_message(bot, callback, "Какая то ошибка. Попробуйте еще раз позже", reply_markup=single_command_button_keyboard())
