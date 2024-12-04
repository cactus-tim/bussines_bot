from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date

from aiogram.utils.deep_linking import create_start_link
from cryptography.fernet import Fernet

from handlers.error import safe_send_message, make_short_link
from bot_instance import bot
from database.req import (get_user, create_user, add_vacancy, delete_vacancy, get_users_tg_id, get_all_events,
                          get_users_tg_id_in_event, get_random_user_from_event, update_event,
                          get_random_user_from_event_wth_bad, get_all_vacancy_names, get_event, get_all_events_in_p,
                          create_event, get_users_tg_id_in_event_bad, update_user_x_event_row_status, get_add_winner,
                          get_users_unreg_tg_id, get_host, get_all_hosts_in_event_orgs, create_host,
                          get_host_by_org_name, update_strick)
from keyboards.keyboards import post_target, post_ev_tagret, stat_target, apply_winner, vacancy_selection_keyboard, \
    single_command_button_keyboard, link_ikb, yes_no_link_ikb, unreg_yes_no_link_ikb, get_ref_ikb, conf_ikb
from statistics.stat import get_stat_all, get_stat_all_in_ev, get_stat_quest, get_stat_ad_give_away, get_stat_reg_out, \
    get_stat_reg

router = Router()


class EventCreateState(StatesGroup):
    waiting_event_name = State()
    waiting_event_date = State()
    waiting_event_time = State()
    waiting_event_place = State()
    waiting_links_count = State()


@router.message(Command("add_event"))
async def cmd_add_event(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, "Введите полное названиве события")
    await state.set_state(EventCreateState.waiting_event_name)


@router.message(EventCreateState.waiting_event_name)
async def add_event_part_2(message: Message, state: FSMContext):
    await state.update_data({'desc': message.text})
    await safe_send_message(bot, message, "Введите дату проведения события в формате DD.MM.YY")
    await state.set_state(EventCreateState.waiting_event_date)


month = {
    1: " января",
    2: " февраля",
    3: " марта",
    4: " апреля",
    5: " мая",
    6: " июня",
    7: " июля",
    8: " августа",
    9: " сентября",
    10: " октября",
    11: " ноября",
    12: " декабря"
}


@router.message(EventCreateState.waiting_event_date)
async def add_event_part_3(message: Message, state: FSMContext):
    data = await state.get_data()
    desc = data.get('desc')
    name = "event" + message.text.replace('.', '_')
    dat = (message.text.split('.')[0] if message.text.split('.')[0][0] != '0' else message.text.split('.')[0][1]) + '' + month[int((message.text.split('.')[1] if message.text.split('.')[1][0] != '0' else message.text.split('.')[1][1]))]
    # dat = date(int(message.text.split('.')[2]), int(message.text.split('.')[1]), int(message.text.split('.')[0]))
    await create_event(name, {'desc': desc, 'date': dat})
    await safe_send_message(bot, message, 'Отправьте время проведение мероприятия')
    await state.update_data({'name': name})
    await state.set_state(EventCreateState.waiting_event_time)


@router.message(EventCreateState.waiting_event_time)
async def add_event_part_4(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    await update_event(name, {'time': message.text})
    await safe_send_message(bot, message, 'Отправьте место проведение мероприятия')
    await state.set_state(EventCreateState.waiting_event_place)


@router.message(EventCreateState.waiting_event_place)
async def add_event_part_5(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    await update_event(name, {'place': message.text})
    await safe_send_message(bot, message, 'Введи количество ссылок для регистрации, которое вам нужно')
    await state.set_state(EventCreateState.waiting_links_count)


async def is_number_in_range(s):
    try:
        num = float(s)
        return True
    except ValueError:
        return False


@router.message(EventCreateState.waiting_links_count)
async def add_event_part_6(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    links = ''
    if not await is_number_in_range(message.text):
        await safe_send_message(bot, message, 'Введи число от 1 до 20')
        return
    for i in range(1, int(message.text) + 1):
        data1 = f'reg_{name}_{i}'
        links += f"https://t.me/HSE_SPB_Business_Club_Bot?start={data1}\n"  # TODO: after 04_12 event links += await create_start_link(bot, data1, encode=True) + '\n'
    data2 = name
    url2 = f"https://t.me/HSE_SPB_Business_Club_Bot?start={data2}"  # TODO: after 04_12 event url2 = await create_start_link(bot, data2, encode=True)
    await safe_send_message(bot, message, f"все круто, все создано!!\nсслыки для регистрации:"
                                          f"\n{links}"
                                          f"\nссылка для подтверждения:"
                                          f"\n{url2}",
                            reply_markup=single_command_button_keyboard())
    await state.clear()


class EventState(StatesGroup):
    waiting_ev = State()
    waiting_ev_for_link = State()
    waiting_links_count = State()


@router.message(Command("get_link"))
async def get_link(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    events = await get_all_events_in_p()
    if not events:
        await safe_send_message(bot, message, 'У вас нет событий((')
    await safe_send_message(bot, message, text="Выберете событие", reply_markup=post_ev_tagret(events))
    await state.set_state(EventState.waiting_ev_for_link)


@router.message(EventState.waiting_ev_for_link)
async def make_link_05(message: Message, state: FSMContext):
    await state.update_data({'name': message.text})
    await safe_send_message(bot, message, 'Введи количество ссылок для регистрации, которое вам нужно')
    await state.set_state(EventState.waiting_links_count)


@router.message(EventState.waiting_links_count)
async def make_link(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get('name')
    links = ''
    if not await is_number_in_range(message.text):
        await safe_send_message(bot, message, 'Введи число от 1 до 20')
        return
    for i in range(1, int(message.text) + 1):
        data1 = f'reg_{name}_{i}'
        links += f"https://t.me/HSE_SPB_Business_Club_Bot?start={data1}\n"  # TODO: after 04_12 event links += await create_start_link(bot, data1, encode=True) + '\n'
    data2 = name
    url2 = f"https://t.me/HSE_SPB_Business_Club_Bot?start={data2}"  # TODO: after 04_12 event url2 = await create_start_link(bot, data2, encode=True)
    await safe_send_message(bot, message, f"все круто, все создано!!\nсслыки для регистрации:"
                                          f"\n{links}"
                                          f"\nссылка для подтверждения:"
                                          f"\n{url2}",
                            reply_markup=single_command_button_keyboard())
    await state.clear()


@router.message(Command("end_event"))
async def cmd_end_event(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    events = await get_all_events_in_p()
    if not events:
        await safe_send_message(bot, message, "Нет актиыных событий(")
        return
    await safe_send_message(bot, message, text="Выберете событие", reply_markup=post_ev_tagret(events))
    await state.set_state(EventState.waiting_ev)


@router.message(EventState.waiting_ev)
async def process_end_event(message: Message, state: FSMContext):
    user_id = await get_random_user_from_event(message.text)
    await state.update_data(event_name=message.text)
    await state.update_data(user_id=user_id)
    bad_ids = []
    await state.update_data(bad_ids=bad_ids)
    user = await get_user(user_id)
    if user == "not created":
        await safe_send_message(bot, message, text="Какие то проблемы, попробуйте заново")
        await state.clear()
        return
    await safe_send_message(bot, message, text=f"Предварительный победитель - @{user.handler}, проверьте его наличие в "
                                               f"аудитории", reply_markup=apply_winner())


@router.callback_query(F.data == "reroll")
async def reroll_end_event(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    bad_ids = data.get("bad_ids")
    user_id = data.get("user_id")
    event_name = data.get("event_name")
    bad_ids.append(user_id)
    user_id = await get_random_user_from_event_wth_bad(event_name, bad_ids)
    await state.update_data(bad_ids=bad_ids)
    await state.update_data(user_id=user_id)
    user = await get_user(user_id)
    if user == "not created":
        await safe_send_message(bot, callback, text="Какие то проблемы, попробуйте заново")
        await state.clear()
        return
    await safe_send_message(bot, callback,
                            text=f"Предварительный победитель - @{user.handler}, проверьте его наличие в "
                                 f"аудитории", reply_markup=apply_winner())


@router.callback_query(F.data == "confirm")
async def confirm_end_event(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Отличное, рассылаю все информацию")
    data = await state.get_data()
    event_name = data.get("event_name")
    user_id = data.get("user_id")
    await update_event(event_name, {'winner': user_id, "status": "end"})
    user = await get_user(user_id)
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, user_id, text=f"У вас нет пользоватеkей))",
                                reply_markup=single_command_button_keyboard())
    else:
        for user_id in user_ids:
            await safe_send_message(bot, user_id, text=f"Сегодняшний победитель - @{user.handler}",
                                    reply_markup=single_command_button_keyboard())
    bad_user_ids = await get_users_tg_id_in_event_bad(event_name)
    if bad_user_ids:
        for user_id in bad_user_ids:
            await update_strick(user_id, 0)
            await update_user_x_event_row_status(user_id, event_name, 'nbeen')
    await safe_send_message(bot, callback, 'Готово')
    await state.clear()


class VacancyState(StatesGroup):
    waiting_for_vacancy_name = State()
    waiting_for_vacancy_name_to_delete = State()


@router.message(Command("all_vacancies"))
async def cmd_all_vacancies(message: Message):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    vacancies = await get_all_vacancy_names()
    if not vacancies:
        await safe_send_message(bot, message, text="У вас нет активных вакансий")
        return
    msg = "Вот все доступные вакансии на данный момент:\n"
    for v in vacancies:
        msg += v + '\n'
    await safe_send_message(bot, message, text=msg, reply_markup=single_command_button_keyboard())


@router.message(Command("add_vacancy"))
async def cmd_add_vacancy(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Введите название вакансии")
    await state.set_state(VacancyState.waiting_for_vacancy_name)


@router.message(VacancyState.waiting_for_vacancy_name)
async def process_vacancy_name(message: Message, state: FSMContext):
    if message.text.lower() == "стоп":
        await state.clear()
        return
    vacancy_name = message.text
    resp = await add_vacancy(vacancy_name)
    if not resp:
        await message.answer(f"Вакансия с именем '{vacancy_name}' уже существует.\n"
                             f"Если хотите добавить другую - напишите ее название.\n"
                             f"Если не хотите напишите \"стоп\"")
    else:
        await message.answer(f"Вакансия '{vacancy_name}' успешно добавлена.",
                             reply_markup=single_command_button_keyboard())
        await state.clear()


@router.message(Command("dell_vacancy"))
async def cmd_dell_vacancy(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    vacancies = await get_all_vacancy_names()
    await safe_send_message(bot, message, text="Выберете название вакансии, которую вы хотите удалить",
                            reply_markup=vacancy_selection_keyboard(vacancies))
    await state.set_state(VacancyState.waiting_for_vacancy_name_to_delete)


@router.message(VacancyState.waiting_for_vacancy_name_to_delete)
async def process_vacancy_name_to_delete(message: Message, state: FSMContext):
    vacancy_name = message.text
    resp = await delete_vacancy(vacancy_name)
    if not resp:
        await message.answer(f"Вакансии '{vacancy_name}' нет.", reply_markup=single_command_button_keyboard())
        await state.clear()
    await message.answer(f"Вакансия '{vacancy_name}' успешно удалена.", reply_markup=single_command_button_keyboard())
    await state.clear()


class PostState(StatesGroup):
    waiting_for_post_to_all_text1 = State()
    waiting_for_post_to_all_text05 = State()
    waiting_for_post_to_all_text = State()
    waiting_for_post_to_ev_ev_unreg = State()
    waiting_for_post_to_all_text1_unreg = State()
    waiting_for_post_to_all_text05_unreg = State()
    waiting_for_post_to_all_text_unreg = State()
    waiting_for_post_to_ev_ev = State()
    waiting_for_post_to_ev_text = State()
    waiting_for_post_wth_op_to_ev_ev = State()
    waiting_for_post_wth_op_to_ev_text = State()


@router.message(Command("send_post"))
async def cmd_send_post(message: Message):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Выберете кому вы хотите отправить пост", reply_markup=post_target())


@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.delete_message(callback.from_user.id, callback.message.message_id - 1)
    await state.clear()
    return


@router.callback_query(F.data == "post_to_unreg")
async def choose_event(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(bot, callback, text="Выберете событие:\n\nДля отмены введите quit",
                            reply_markup=post_ev_tagret(events))
    await state.set_state(PostState.waiting_for_post_to_ev_ev_unreg)


@router.message(PostState.waiting_for_post_to_ev_ev_unreg)
async def mb_add_link_unreg(message: Message, state: FSMContext):
    await state.update_data({'event_name': message.text})
    await safe_send_message(bot, message, "Хочешь добавить к посту кнопку с ссылкой?", unreg_yes_no_link_ikb())


@router.callback_query(F.data == "unreg_link_no")
async def link_no_unreg(callback: CallbackQuery, state: FSMContext):
    await state.update_data({'flag': False})
    await safe_send_message(bot, callback, text="Отправьте мне пост")
    await state.set_state(PostState.waiting_for_post_to_all_text_unreg)


@router.callback_query(F.data == "unreg_link_yes")
async def link_yes_unreg(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Отправь мне ссылку\n\nДля отмены введите quit")
    await state.set_state(PostState.waiting_for_post_to_all_text05_unreg)


@router.message(PostState.waiting_for_post_to_all_text05_unreg)
async def cmd_post_to_all_unreg(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await state.update_data({'link': message.text, 'flag': True})
    await safe_send_message(bot, message, text="Отправь надпись на кнопке\n\nДля отмены введите quit")
    await state.set_state(PostState.waiting_for_post_to_all_text1_unreg)


@router.message(PostState.waiting_for_post_to_all_text1_unreg)
async def cmd_post_to_all_unreg(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await state.update_data({'text': message.text})
    await safe_send_message(bot, message, text="Отправьте мне пост\n\nДля отмены введите quit")
    await state.set_state(PostState.waiting_for_post_to_all_text_unreg)


@router.message(PostState.waiting_for_post_to_all_text_unreg)
async def process_post_to_all_unreg(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    data = await state.get_data()
    event_name = data.get('event_name')
    flag = data.get('flag')
    user_ids = await get_users_unreg_tg_id(event_name)
    if flag:
        link = data.get('link')
        text = data.get('text')
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей((",
                                reply_markup=single_command_button_keyboard())
        return
    for user_id in user_ids:
        if flag:
            await safe_send_message(bot, user_id, text=message.text, reply_markup=(single_command_button_keyboard() if not flag else link_ikb(text, link)))
    await safe_send_message(bot, message, "Готово", reply_markup=single_command_button_keyboard())
    await state.clear()


@router.callback_query(F.data == "post_to_all")
async def mb_add_link(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, "Хочешь добавить к посту кнопку с ссылкой?", yes_no_link_ikb())


@router.callback_query(F.data == "link_no")
async def link_no(callback: CallbackQuery, state: FSMContext):
    await state.update_data({'flag': False})
    await safe_send_message(bot, callback, text="Отправьте мне пост")
    await state.set_state(PostState.waiting_for_post_to_all_text)


@router.callback_query(F.data == "link_yes")
async def link_yes(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Отправь мне ссылку\n\nДля отмены введите quit")
    await state.set_state(PostState.waiting_for_post_to_all_text05)


@router.message(PostState.waiting_for_post_to_all_text05)
async def cmd_post_to_all(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await state.update_data({'link': message.text, 'flag': True})
    await safe_send_message(bot, message, text="Отправь надпись на кнопке\n\nДля отмены введите quit")
    await state.set_state(PostState.waiting_for_post_to_all_text1)


@router.message(PostState.waiting_for_post_to_all_text1)
async def cmd_post_to_all(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await state.update_data({'text': message.text})
    await safe_send_message(bot, message, text="Отправьте мне пост\n\nДля отмены введите quit")
    await state.set_state(PostState.waiting_for_post_to_all_text)


@router.message(PostState.waiting_for_post_to_all_text)
async def process_post_to_all(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    user_ids = await get_users_tg_id()
    data = await state.get_data()
    flag = data.get('flag')
    if flag:
        link = data.get('link')
        text = data.get('text')
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей((",
                                reply_markup=single_command_button_keyboard())
        return
    for user_id in user_ids:
        if flag:
            await safe_send_message(bot, user_id, text=message.text, reply_markup=(single_command_button_keyboard() if not flag else link_ikb(text, link)))
    await safe_send_message(bot, message, "Готово", reply_markup=single_command_button_keyboard())
    await state.clear()


@router.callback_query(F.data == "post_to_ev")
async def cmd_post_to_ev(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(bot, callback, text="Выберете событие:\n\nДля отмены введите quit", reply_markup=post_ev_tagret(events))
    await state.set_state(PostState.waiting_for_post_to_ev_ev)


@router.message(PostState.waiting_for_post_to_ev_ev)
async def pre_process_post_to_ev(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await safe_send_message(bot, message, text="Отправьте мне пост\n\nДля отмены введите quit")
    await state.update_data(event_name=message.text)
    await state.set_state(PostState.waiting_for_post_to_ev_text)


@router.message(PostState.waiting_for_post_to_ev_text)
async def process_post_to_ev(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей принявших участие в этом событии",
                                reply_markup=single_command_button_keyboard())
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=message.text, reply_markup=single_command_button_keyboard())
    await safe_send_message(bot, message, "Готово", reply_markup=single_command_button_keyboard())
    await state.clear()


# https://chatgpt.com/share/673d7302-fcc0-8004-877f-11760ff426f4
@router.callback_query(F.data == "post_wth_op_to_ev")
async def cmd_post_to_ev(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(bot, callback, text="Выберете событие:\n\nДля отмены введите quit", reply_markup=post_ev_tagret(events))
    await state.set_state(PostState.waiting_for_post_wth_op_to_ev_ev)


@router.message(PostState.waiting_for_post_wth_op_to_ev_ev)
async def pre_process_post_to_ev(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await safe_send_message(bot, message, text="Отправьте мне ссылку на гугл-форму\n\nДля отмены введите quit")
    await state.update_data(event_name=message.text)
    await state.set_state(PostState.waiting_for_post_wth_op_to_ev_text)


msg = """
Привет! 
Благодарим за посещение нашего мероприятия! 🔥

Мы хотим становиться лучше, поэтому нам, как всегда, очень нужна твоя обратная связь 🤝

Поделись парочкой слов о том, что понравилось, а что можно улучшить, по ссылке ниже 👇
"""


@router.message(PostState.waiting_for_post_wth_op_to_ev_text)
async def process_post_to_wth_op_to_ev(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей принявших участие в этом событии",
                                reply_markup=single_command_button_keyboard())
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=msg, reply_markup=link_ikb('Форма обратной связи', message.text))
    await safe_send_message(bot, message, "Готово", reply_markup=single_command_button_keyboard())
    await state.clear()


class StatState(StatesGroup):
    waiting_for_ev = State()
    waiting_for_give_away_ev = State()
    waiting_user_id = State()
    waiting_for_ev1 = State()
    waiting_for_ev2 = State()


@router.message(Command("send_stat"))
async def cmd_send_stat(message: Message):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Выберете какую статистику вы хотите получить",
                            reply_markup=stat_target())


@router.callback_query(F.data == "stat_all")
async def cmd_stat_all(callback: CallbackQuery):
    await get_stat_all(callback.from_user.id)


@router.callback_query(F.data == "stat_ev")
async def cmd_stat_ev(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(StatState.waiting_for_ev)


@router.message(StatState.waiting_for_ev)
async def process_post_to_all(message: Message, state: FSMContext):
    await get_stat_all_in_ev(message.from_user.id, message.text)
    await state.clear()


@router.callback_query(F.data == "stat_quest")
async def cmd_stat_ev(callback: CallbackQuery):
    await get_stat_quest(callback.from_user.id)


@router.callback_query(F.data == 'stat_give_away')
async def cmd_stat_give_away(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(StatState.waiting_for_give_away_ev)


@router.message(StatState.waiting_for_give_away_ev)
async def cmd_stat_give_away2(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await state.clear()
        return
    await state.update_data({'event_name': message.text})
    await safe_send_message(bot, message, 'Введите юзер id организатора дополнительного розыгрыша\n\nДля отмены введите quit')
    await state.set_state(StatState.waiting_user_id)


@router.message(StatState.waiting_user_id)
async def cmd_stat_give_away3(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await state.clear()
        return
    data = await state.get_data()
    event_name = data.get('event_name')
    await get_stat_ad_give_away(message.from_user.id, int(message.text), event_name)
    await state.clear()


@router.callback_query(F.data == 'stat_reg_out')
async def cmd_stat_reg(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(StatState.waiting_for_ev1)


@router.message(StatState.waiting_for_ev1)
async def cmd_stat_reg2(message: Message, state: FSMContext):
    await get_stat_reg_out(message.from_user.id, message.text)
    await state.clear()


@router.callback_query(F.data == 'stat_reg')
async def cmd_stat_reg(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(StatState.waiting_for_ev2)


@router.message(StatState.waiting_for_ev2)
async def cmd_stat_reg2(message: Message, state: FSMContext):
    await get_stat_reg(message.from_user.id, message.text)
    await state.clear()


class WinnerState(StatesGroup):
    wait_give_away_event = State()
    wait_give_away_id = State()


@router.message(Command('get_result'))
async def cmd_get_result(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, message, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, message, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(WinnerState.wait_give_away_event)


@router.message(WinnerState.wait_give_away_event)
async def get_result(message: Message, state: FSMContext):
    await state.update_data({'event_name': message.text})
    hosts_orgs = await get_all_hosts_in_event_orgs(message.text)
    if not hosts_orgs:
        await safe_send_message(bot, message, text="У вас нет организаторов дополнительных розыгрышей", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, message, text="Выберете организатора:\n\nДля отмены введите quit'", reply_markup=post_ev_tagret(hosts_orgs))
    await state.set_state(WinnerState.wait_give_away_id)


@router.message(WinnerState.wait_give_away_id)
async def get_result2(message: Message, state: FSMContext):
    data = await state.get_data()
    event_name = data.get('event_name')
    if message.text.lower() == 'quit':
        await state.clear()
        return
    host = await get_host_by_org_name(message.text, event_name)
    winner_id = await get_add_winner(host.user_id, event_name)
    if not winner_id:
        await safe_send_message(bot, message, 'В этом розыгрыше нет участников((')
        await state.clear()
        return
    winner = await get_user(winner_id)
    await safe_send_message(bot, message, f'@{winner.handler} - победитель розыгрыша от @{host.org_name}')


class GiveAwayState(StatesGroup):
    waiting_event = State()
    waiting_org_name = State()
    waiting_id = State()


@router.message(Command('create_give_away'))
async def cmd_create_give_away(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, message, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, message, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(GiveAwayState.waiting_event)


@router.message(GiveAwayState.waiting_event)
async def cmd_create_give_away2(message: Message, state: FSMContext):
    await state.update_data({'event_name': message.text})
    await safe_send_message(bot, message, 'Введите название организации\n\nДля отмены введите quit')
    await state.set_state(GiveAwayState.waiting_org_name)


@router.message(GiveAwayState.waiting_org_name)
async def cmd_create_give_away3(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await state.clear()
        return
    await state.update_data({'org_name': message.text})
    await safe_send_message(bot, message, 'Введите айди организатора\n\nЕсли хотите использовать свое айди = отправьте Я\n\nДля отмены введите quit')
    await state.set_state(GiveAwayState.waiting_id)


@router.message(GiveAwayState.waiting_id)
async def cmd_create_give_away4(message: Message, state: FSMContext):
    if message.text.lower() == 'quit':
        await state.clear()
        return
    data = await state.get_data()
    event_name = data.get('event_name')
    org_name = data.get('org_name')
    user_id = message.from_user.id if message.text.lower() == 'я' else message.text
    if not await is_number_in_range(user_id):
        await safe_send_message(bot, message, 'Введи число - айди')
        return
    user_id = int(user_id)
    await create_host(user_id, event_name, org_name)
    await safe_send_message(bot, message, 'Готово!', reply_markup=get_ref_ikb(event_name))
    await state.clear()


@router.message(Command('ss1'))
async def pupupu(message: Message):
    user_ids = await get_users_tg_id_in_event('event04_12_24')
    for user_id in user_ids:
        await safe_send_message(bot, user_id, 'Внимание ⚠️\nПосле 18:05 вход в зал будет закрыт. Это сделано, чтобы не мешать выступлению спикера.')
    await safe_send_message(bot, message, 'ss')

