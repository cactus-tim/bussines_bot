from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile

from bot_instance import bot
from database.req import get_user, create_user, create_user_x_event_row, get_all_user_events, get_event, \
    update_user_x_event_row_status, update_reg_event, check_completly_reg_event, create_reg_event, get_reg_event, \
    get_user_x_event_row, get_ref_give_away, create_ref_give_away, delete_user_x_event_row, delete_ref_give_away_row, \
    get_all_hosts_in_event_ids, get_host, add_money, one_more_event, get_user_rank_by_money, get_top_10_users_by_money, \
    add_referal_cnt, update_strick, add_user_to_networking, create_qr_code
from handlers.error import safe_send_message
from handlers.qr_utils import create_styled_qr_code
from handlers.quest import start
from keyboards.keyboards import single_command_button_keyboard, events_ikb, yes_no_ikb, yes_no_hse_ikb, get_ref_ikb, \
    top_ikb

router = Router()


class EventReg(StatesGroup):
    waiting_name = State()
    waiting_surname = State()
    waiting_fathername = State()
    waiting_mail = State()
    waiting_phone = State()
    waiting_org = State()


give_away_ids = {1568674379: 'hsespbcareer',
                 1426453089: 'Коляна',
                 483458201: 'Me. Only for tests'}

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
    hash_value = command.args

    if hash_value and hash_value.startswith('qr_'):
        # Create a new command object for check_qr
        check_qr_command = CommandObject(command=message.text, args=hash_value)
        await cmd_check_qr(message, check_qr_command)
        return

    user = await get_user(message.from_user.id)
    if hash_value:
        if hash_value == 'networking':
            if user == "not created":
                user = await create_user(message.from_user.id,
                                         {'handler': message.from_user.username, 'first_contact': hash_value})
            flag = await add_user_to_networking(message.from_user.id)
            if not flag:
                await safe_send_message(bot, message.from_user.id, 'Вы уже участвуете в нетворкинге')
            else:
                await safe_send_message(bot, message.from_user.id, 'Поздравляем! Вы участвуете в нетворкинге')
            await bot.delete_message(message.from_user.id, message.message_id - 1)
        elif hash_value[:3] == 'reg':
            if user == "not created":
                user = await create_user(message.from_user.id,
                                         {'handler': message.from_user.username, 'first_contact': hash_value[4:]})
            # await safe_send_message(bot, message.from_user.id,
            #                         text=mmsg,
            #                         reply_markup=single_command_button_keyboard())
            event_name = hash_value.split('_')[1] + '_' + hash_value.split('_')[2] + '_' + hash_value.split('_')[3]
            user_x_event = await get_user_x_event_row(message.from_user.id, event_name)
            if user_x_event == 'not created':
                await create_user_x_event_row(message.from_user.id, event_name, hash_value.split('_')[-1])
                event = await get_event(event_name)
                if event == 'not created':
                    await safe_send_message(bot, message, 'Такого события не существует..')
                await state.update_data({'name': event_name})
                await safe_send_message(bot, message, f'Хотите зарегистрироваться на мероприятие "{event.desc}",'
                                                      f'которое пройдет {event.date} в {event.time}',
                                        reply_markup=yes_no_ikb())
            else:
                await safe_send_message(bot, message, 'Вы уже зарегистрировались на это мероприятие',
                                        reply_markup=get_ref_ikb(event_name))
        elif hash_value[:3] == 'ref':
            if hash_value[3] == '_':
                event_part, user_id = hash_value.split("__")
                event_name = event_part.replace("ref_", "")
                user_id = int(user_id)
                if user == "not created":
                    user = await create_user(message.from_user.id,
                                             {'handler': message.from_user.username, 'first_contact': str(user_id)})
                # await safe_send_message(bot, message.from_user.id,
                #                         text=mmsg,
                #                         reply_markup=single_command_button_keyboard())
                user_x_event = await get_user_x_event_row(message.from_user.id, event_name)
                if user_x_event == 'not created':
                    await create_user_x_event_row(message.from_user.id, event_name, str(user_id))
                    event = await get_event(event_name)
                    if event == 'not created':
                        await safe_send_message(bot, message, 'Такого события не существует..')
                    await state.update_data({'name': event_name})
                    await safe_send_message(bot, message, f'Хотите зарегистрироваться на мероприятие "{event.desc}",'
                                                          f'которое пройдет {event.date} в {event.time}',
                                            reply_markup=yes_no_ikb())
                    hosts_ids = await get_all_hosts_in_event_ids(event_name)
                    if hosts_ids and user_id in hosts_ids:
                        ref_give_away = await get_ref_give_away(message.from_user.id, event_name)
                        if not ref_give_away:
                            await create_ref_give_away(message.from_user.id, event_name, user_id)
                            host = await get_host(user_id, event_name)
                            await safe_send_message(bot, message,
                                                    f'Поздравляю, вы участвуете в розыгрыше, предназначенным только для подписчиков @{host.org_name}')
                        else:
                            await safe_send_message(bot, message, 'Вы уже участвуете в чьем то розыгрыше')
                    await safe_send_message(bot, user_id, f"По твоей реферальной ссылке зарегистрировался на событие"
                                                          f" пользователь @{message.from_user.username}!")
                else:
                    await safe_send_message(bot, message, 'Вы уже зарегистрировались на это мероприятие',
                                            reply_markup=get_ref_ikb(event_name))
        elif hash_value == 'otbor':
            if user == "not created":
                user = await create_user(message.from_user.id,
                                         {'handler': message.from_user.username, 'first_contact': hash_value})
            name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
            await safe_send_message(bot, message, f'Привет, {name}!', reply_markup=single_command_button_keyboard())
            await start(message)
        else:
            if user == "not created":
                user = await create_user(message.from_user.id,
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
            row = await update_user_x_event_row_status(message.from_user.id, hash_value, 'been')
            if not row:
                await create_user_x_event_row(message.from_user.id, hash_value, '0')
                row = await update_user_x_event_row_status(message.from_user.id, hash_value, 'been')
            await add_money(message.from_user.id, 1)
            await one_more_event(message.from_user.id)
            await update_strick(message.from_user.id)
            ref_giver = await get_user(int(row.first_contact))
            await safe_send_message(bot, message, text="QR-код удачно отсканирован!",
                                    reply_markup=single_command_button_keyboard())
            hosts_ids = await get_all_hosts_in_event_ids(hash_value)
            if (not hosts_ids and ref_giver != 'not created') or (
                    hosts_ids and ref_giver != 'not created' and ref_giver.id not in hosts_ids):
                await safe_send_message(bot, ref_giver.id,
                                        f'Вы получили 2 монетки за то что приглашенный вами человек @{user.handler} посетил событие!')
                await add_money(ref_giver.id, 2)
                await add_referal_cnt(ref_giver.id)
                await safe_send_message(bot, message.from_user.id,
                                        f'Вы получили монетку за то что вы зарегистрировались по реферальной ссылке @{ref_giver.handler}!')
                await add_money(message.from_user.id, 1)
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
    await safe_send_message(bot, message, 'Используйте /info чтобы получить информацию о доступных командах')
    # TODO: to del after bets


@router.callback_query(F.data == "event_no")
async def reg_event_part0_5(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, "Это очень грустно((", reply_markup=single_command_button_keyboard())
    data = await state.get_data()
    event_name = data.get('name')
    row = await get_user_x_event_row(callback.from_user.id, event_name)
    if row != "not created":
        await delete_user_x_event_row(callback.from_user.id, event_name)
    row = await get_ref_give_away(callback.from_user.id, event_name)
    if row:
        await delete_ref_give_away_row(callback.from_user.id, event_name)
    await state.clear()


@router.callback_query(F.data == "event_yes")
async def reg_event_part1(callback: CallbackQuery, state: FSMContext):
    """Handle event registration confirmation."""
    await safe_send_message(bot, callback, "Вы студент/сотрудник НИУ ВШЭ?", reply_markup=yes_no_hse_ikb())


@router.callback_query(F.data == "hse_yes")
async def reg_event_part1_5(callback: CallbackQuery, state: FSMContext):
    """Handle HSE student/employee registration."""
    data = await state.get_data()
    name = data.get('name')
    event = await get_event(name)
    await create_user_x_event_row(callback.from_user.id, name, callback.from_user.username)
    bot_username = (await bot.get_me()).username
    qr_data = f"https://t.me/{bot_username}?start=qr_{callback.from_user.id}_{name}"
    qr_image = create_styled_qr_code(qr_data)
    await create_qr_code(callback.from_user.id, name)
    temp_file = "temp_qr.png"
    with open(temp_file, "wb") as f:
        f.write(qr_image.getvalue())
    try:
        await safe_send_message(bot, callback,
                                f"Мы вас ждем на мероприятии \"{event.desc}\", которое пройдет {event.date} в {event.time}\n"
                                f"Место проведение - {event.place}",
                                reply_markup=get_ref_ikb(name)
                                )
        await callback.message.answer_photo(
            photo=FSInputFile(temp_file),
            caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                    f"Это ваш пропуск на мероприятие:\n"
                    f"Название: {event.desc}\n"
                    f"Дата: {event.date}\n"
                    f"Время: {event.time}\n"
                    f"Место: {event.place}\n\n"
                    f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
        )
    finally:
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)
    await state.clear()


@router.callback_query(F.data == "hse_no")
async def reg_event_part2(callback: CallbackQuery, state: FSMContext):
    """Handle non-HSE user registration."""
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
        await create_user_x_event_row(callback.from_user.id, name, callback.from_user.username)
        bot_username = (await bot.get_me()).username
        qr_data = f"https://t.me/{bot_username}?start=qr_{callback.from_user.id}_{name}"
        qr_image = create_styled_qr_code(qr_data)
        await create_qr_code(callback.from_user.id, name)
        temp_file = "temp_qr.png"
        with open(temp_file, "wb") as f:
            f.write(qr_image.getvalue())
        try:
            await safe_send_message(bot, callback,
                                    "Ваши данные уже сохранены!\n"
                                    f"Мы вас ждем на мероприятии \"{event.desc}\", которое пройдет {event.date} в {event.time}\n"
                                    f"Место проведение - {event.place}",
                                    reply_markup=get_ref_ikb(name)
                                    )
            await callback.message.answer_photo(
                photo=FSInputFile(temp_file),
                caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                        f"Это ваш пропуск на мероприятие:\n"
                        f"Название: {event.desc}\n"
                        f"Дата: {event.date}\n"
                        f"Время: {event.time}\n"
                        f"Место: {event.place}\n\n"
                        f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
            )
        finally:
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
        await state.clear()
    else:
        await safe_send_message(bot, callback,
                                "Для пропуска на мероприятие нужно будет сообщить ваши данные. Напишите, пожалуйста, ваше имя")
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
    """Handle organization input and complete registration."""
    await update_reg_event(message.from_user.id, {'org': message.text})
    if await check_completly_reg_event(message.from_user.id):
        data = await state.get_data()
        name = data.get('name')
        event = await get_event(name)
        await create_user_x_event_row(message.from_user.id, name, message.from_user.username)
        bot_username = (await bot.get_me()).username
        qr_data = f"https://t.me/{bot_username}?start=qr_{message.from_user.id}_{name}"
        qr_image = create_styled_qr_code(qr_data)
        await create_qr_code(message.from_user.id, name)
        temp_file = "temp_qr.png"
        with open(temp_file, "wb") as f:
            f.write(qr_image.getvalue())
        try:
            await safe_send_message(bot, message,
                                    f"Мы вас ждем на мероприятии \"{event.desc}\", которое пройдет {event.date} в {event.time}\n"
                                    f"Место проведение - {event.place}\n\n"
                                    f"⚠ Обязательно возьмите с собой паспорт!",
                                    reply_markup=get_ref_ikb(name)
                                    )
            await message.answer_photo(
                photo=FSInputFile(temp_file),
                caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                        f"Это ваш пропуск на мероприятие:\n"
                        f"Название: {event.desc}\n"
                        f"Дата: {event.date}\n"
                        f"Время: {event.time}\n"
                        f"Место: {event.place}\n\n"
                        f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
            )
        finally:
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
    else:
        await safe_send_message(bot, message, 'Что то пошло не так, начните регистрацию заново, пожалуйста\n'
                                              'Для этого повторно перейдите по ссылке')
    await state.clear()


@router.message(Command("info"))
async def cmd_info(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(bot, message, text="Список доступных команд:\n"
                                                   "/start - перезапуск бота\n"
                                                   "/info - информация о доступных командах\n"
                                                   "/quest - пройти анкетирование для отбора в команду\n"
                                                   "/get_ref - получить реферальную ссылку на событие\n"
                                                   "/profile - ваш профиль со всей информацией о вас\n"
                                                   "/top - топ 10 по владению монетками\n"
                                                   "/my_qr - получить QR код для последнего мероприятия\n"
                                                   "/send_stat - получить статистику о пользователях\n"
                                                   "/send_post - отправить пост пользователям\n"
                                                   "/add_event - создает новое событие\n"
                                                   "/end_event - завершить событие\n"
                                                   "/get_link - получить ссылки на событие\n"
                                                   "/create_give_away - создать дополнительный розыгрыш для инфлюенсера\n"
                                                   "/get_result - получить победителя в дополнительном розыгрыше\n"
                                                   "Инструкция по пользованию ботом https://clck.ru/3EwSJM",
                                reply_markup=single_command_button_keyboard())
    else:
        await safe_send_message(bot, message, text="Список доступных команд:\n"
                                                   "/start - перезапуск бота\n"
                                                   "/info - информация о доступных командах\n"
                                                   "/quest - пройти анкетирование для отбора в команду\n"
                                                   "/get_ref - получить реферальную ссылку на событие\n"
                                                   "/profile - ваш профиль со всей информацией о вас\n"
                                                   "/top - топ 10 по владению монетками\n"
                                                   "/my_qr - получить QR код для последнего мероприятия\n")


@router.message(Command('profile'))
async def cmd_profile(message: Message):
    user = await get_user(message.from_user.id)
    name = message.from_user.first_name if message.from_user.first_name else message.from_user.username
    rank = await get_user_rank_by_money(message.from_user.id)
    msg = f'Твой личный кабинет\n\nКоличество посещенных мероприятий: {user.event_cnt}\nКоличество посещенных мероприятий подряд: {user.strick}\nКоличество рефералов: {user.ref_cnt}\nКоличество монеток: {user.money}\nМесто в топе: {rank}'
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


@router.callback_query(F.data.startswith("verify_"))
async def process_verification(callback: CallbackQuery):
    """Handle QR code verification by admin."""
    try:
        # Print the callback data for debugging
        print(f"Callback data: {callback.data}")

        # Split the callback data to get user_id, event_name and action
        parts = callback.data.split('_')
        print(f"Split parts: {parts}")  # Debug print

        if len(parts) < 4:
            await callback.answer("Неверный формат данных")
            return

        # The first part is 'verify', then user_id, then event_name (which may contain underscores)
        # and finally the action (allow/deny)
        verify_prefix = parts[0]
        user_id = parts[1]
        action = parts[-1]  # Last part is always the action

        # Everything in between is the event name
        event_name = '_'.join(parts[2:-1])

        print(
            f"Parsed data: verify_prefix={verify_prefix}, user_id={user_id}, event_name={event_name}, action={action}")  # Debug print

        user_id = int(user_id)

        # Get user and event info
        user = await get_user(user_id)
        event = await get_event(event_name)

        if user == "not created" or event == "not created":
            await callback.answer("Пользователь или мероприятие не найдены")
            return

        # Get user registration details
        reg_event = await get_reg_event(user_id)
        user_info = ""
        if reg_event:
            user_info = f"\nФИО: {reg_event.surname} {reg_event.name} {reg_event.fathername}\nТелефон: {reg_event.phone}"

        if action == "allow":
            # Update user_x_event status to 'been'
            await update_user_x_event_row_status(user_id, event_name, 'been')

            # Add money and update event count
            await add_money(user_id, 1)
            await one_more_event(user_id)
            await update_strick(user_id)

            # Notify admin
            await callback.answer("✅ Пользователь успешно пропущен")

            # Notify user
            await bot.send_message(
                user_id,
                f"Ваш QR код был успешно отсканирован на мероприятии {event.desc}!"
            )

            # Handle referral bonus if applicable
            user_x_event = await get_user_x_event_row(user_id, event_name)
            if user_x_event != "not created" and user_x_event.first_contact != '0':
                ref_giver = await get_user(int(user_x_event.first_contact))
                if ref_giver != "not created":
                    hosts_ids = await get_all_hosts_in_event_ids(event_name)
                    if (not hosts_ids and ref_giver != 'not created') or (
                            hosts_ids and ref_giver != 'not created' and ref_giver.id not in hosts_ids):
                        await safe_send_message(bot, ref_giver.id,
                                                f'Вы получили 2 монетки за то что приглашенный вами человек @{user.handler} посетил событие!')
                        await add_money(ref_giver.id, 2)
                        await add_referal_cnt(ref_giver.id)
                        await safe_send_message(bot, user_id,
                                                f'Вы получили монетку за то что вы зарегистрировались по реферальной ссылке @{ref_giver.handler}!')
                        await add_money(user_id, 1)

            # Update the message with verification result
            await callback.message.edit_text(
                f"✅ Пользователь пропущен:\n"
                f"Пользователь: @{user.handler}{user_info}\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}"
            )
        else:
            # Just notify admin for deny
            await callback.answer("❌ Пользователь не пропущен")
            # Update the message with verification result
            await callback.message.edit_text(
                f"❌ Пользователь не пропущен:\n"
                f"Пользователь: @{user.handler}{user_info}\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}"
            )

    except Exception as e:
        print(f"Verification error: {e}")
        await callback.answer("Произошла ошибка при обработке верификации")


@router.callback_query()
async def get_ref_v2_part2(callback: CallbackQuery):
    """Handle event selection for referral link generation."""
    try:
        event = await get_event(callback.data)
        if event == "not created":
            await callback.answer("Мероприятие не найдено")
            return

        data = f'ref_{callback.data}__{callback.from_user.id}'
        url = f"https://t.me/HSE_SPB_Business_Club_Bot?start={data}"

        await safe_send_message(bot, callback,
                                f"Вот твоя реферальная ссылка для событие {event.desc}:\n{url}",
                                reply_markup=single_command_button_keyboard()
                                )
    except Exception as e:
        print(f"Referral link generation error: {e}")
        await callback.answer("Произошла ошибка при создании реферальной ссылки")


@router.message(Command("my_qr"))
async def cmd_my_qr(message: Message):
    """Handle /my_qr command to get QR code for latest event registration."""
    user = await get_user(message.from_user.id)
    if user == "not created":
        await safe_send_message(bot, message, "Вы не зарегистрированы в боте")
        return

    # Get latest event registration
    events = await get_all_user_events(message.from_user.id)
    if not events:
        await safe_send_message(bot, message, "У вас нет активных регистраций на мероприятия")
        return

    latest_event = events[0]  # Events are ordered by registration time

    # Generate QR code
    bot_username = (await bot.get_me()).username
    qr_data = f"https://t.me/{bot_username}?start=qr_{message.from_user.id}_{latest_event.name}"
    qr_image = create_styled_qr_code(qr_data)

    # Create QR code record
    await create_qr_code(message.from_user.id, latest_event.name)

    # Save QR code to a temporary file
    temp_file = "temp_qr.png"
    with open(temp_file, "wb") as f:
        f.write(qr_image.getvalue())

    try:
        # Send QR code with detailed caption
        await message.answer_photo(
            photo=FSInputFile(temp_file),
            caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                    f"Это ваш пропуск на мероприятие:\n"
                    f"Название: {latest_event.desc}\n"
                    f"Дата: {latest_event.date}\n"
                    f"Время: {latest_event.time}\n"
                    f"Место: {latest_event.place}\n\n"
                    f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
        )
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)


@router.callback_query(F.data == "yes")
async def process_reg_yes(callback: CallbackQuery, state: FSMContext):
    """Handle event registration confirmation."""
    data = await state.get_data()
    event_name = data.get("name")

    # Create registration
    await create_user_x_event_row(callback.from_user.id, event_name, callback.from_user.username)
    event = await get_event(event_name)

    # Generate and send QR code
    bot_username = (await bot.get_me()).username
    qr_data = f"https://t.me/{bot_username}?start=qr_{callback.from_user.id}_{event_name}"
    qr_image = create_styled_qr_code(qr_data)
    await create_qr_code(callback.from_user.id, event_name)

    # Save QR code to a temporary file
    temp_file = "temp_qr.png"
    with open(temp_file, "wb") as f:
        f.write(qr_image.getvalue())

    try:
        await callback.message.answer_photo(
            photo=FSInputFile(temp_file),
            caption=f"Вы успешно зарегистрировались на мероприятие!\n\n"
                    f"Название: {event.desc}\n"
                    f"Дата: {event.date}\n"
                    f"Время: {event.time}\n"
                    f"Место: {event.place}\n\n"
                    f"Покажите этот QR код при входе на мероприятие."
        )
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)

    await state.clear()


@router.message(Command("check_qr"))
async def cmd_check_qr(message: Message, command: CommandObject):
    """Handle QR code verification via command."""
    if not command.args:
        await safe_send_message(bot, message, "Пожалуйста, укажите QR код после команды /check_qr")
        return

    hash_value = command.args
    if not hash_value.startswith('qr_'):
        await safe_send_message(bot, message, "Недействительный QR код")
        return

    try:
        # Split only on first two underscores to preserve event name
        parts = hash_value.split('_', 2)
        if len(parts) != 3:
            await safe_send_message(bot, message, "Недействительный QR код")
            return

        _, user_id, event_name = parts
        user_id = int(user_id)

        # Get user and event info
        user = await get_user(user_id)
        event = await get_event(event_name)

        if user == "not created" or event == "not created":
            await safe_send_message(bot, message, "Недействительный QR код")
            return

        # Check if user is registered for the event
        user_x_event = await get_user_x_event_row(user_id, event_name)
        if user_x_event == "not created":
            await safe_send_message(bot, message, "Пользователь не зарегистрирован на это мероприятие")
            return

        if user_x_event.status not in ['reg', 'been']:
            await safe_send_message(bot, message, "Пользователь не зарегистрирован на это мероприятие")
            return

        # Check if event is in progress
        if event.status != 'in_progress':
            await safe_send_message(bot, message, "Мероприятие не активно")
            return

        # Check if scanner is superuser
        scanner = await get_user(message.from_user.id)
        if scanner.is_superuser:
            # Get user registration details
            reg_event = await get_reg_event(user_id)
            user_info = ""
            if reg_event:
                user_info = f"\nФИО: {reg_event.surname} {reg_event.name} {reg_event.fathername}\nТелефон: {reg_event.phone}"

            # Check if QR code was already used
            if user_x_event.status == 'been':
                await safe_send_message(bot, message,
                                        f"⚠️ Этот QR код уже был использован!\n\n"
                                        f"Пользователь: @{user.handler}{user_info}\n"
                                        f"Мероприятие: {event.desc}\n"
                                        f"Дата: {event.date}\n"
                                        f"Время: {event.time}\n"
                                        f"Место: {event.place}"
                                        )
                return

            # Show verification buttons
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="✅ Пропустить",
                        callback_data=f"verify_{user_id}_{event_name}_allow"
                    ),
                    InlineKeyboardButton(
                        text="❌ Не пропускать",
                        callback_data=f"verify_{user_id}_{event_name}_deny"
                    )
                ]
            ])

            await message.answer(
                f"Проверка QR кода:\n"
                f"Пользователь: @{user.handler}{user_info}\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}",
                reply_markup=keyboard
            )
        else:
            # Check if the QR code belongs to the user who scanned it
            if user_id != message.from_user.id:
                await safe_send_message(bot, message, "⚠️ Это не ваш QR код! Вы можете сканировать только свои QR коды.")
                return

            # Show event info to regular users
            await safe_send_message(bot, message,
                f"Информация о мероприятии:\n"
                f"Название: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}"
            )

    except (ValueError, IndexError) as e:
        print(f"QR code validation error: {e}")
        await safe_send_message(bot, message, "Недействительный QR код")
        return
