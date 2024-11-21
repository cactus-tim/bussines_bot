from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date

from handlers.error import safe_send_message
from bot_instance import bot
from database.req import (get_user, create_user, add_vacancy, delete_vacancy, get_users_tg_id, get_all_events,
                          get_users_tg_id_in_event, get_random_user_from_event, update_event,
                          get_random_user_from_event_wth_bad, get_all_vacancy_names, get_event, get_all_events_in_p,
                          create_event, get_users_tg_id_in_event_bad, update_user_x_event_row_status)
from keyboards.keyboards import post_target, post_ev_tagret, stat_target, apply_winner, vacancy_selection_keyboard, \
    single_command_button_keyboard, feedback_form_ikb
from statistics.stat import get_stat_all, get_stat_all_in_ev, get_stat_quest


router = Router()


class EventCreateState(StatesGroup):
    waiting_event_name = State()
    waiting_event_date = State()


@router.message(Command("add_event"))
async def cmd_add_event(message: Message, state: FSMContext):
    await safe_send_message(bot, message, "Введите полное названиве события")
    await state.set_state(EventCreateState.waiting_event_name)


@router.message(EventCreateState.waiting_event_name)
async def add_event_part_2(message: Message, state: FSMContext):
    await state.update_data({'desc': message.text})
    await safe_send_message(bot, message, "Введите дату проведения события в формате DD.MM.YY")
    await state.set_state(EventCreateState.waiting_event_date)


@router.message(EventCreateState.waiting_event_date)
async def add_event_part_3(message: Message, state: FSMContext):
    data = await state.get_data()
    desc = data.get('desc')
    name = "event" + message.text.replace('.', '_')
    dat = date(int(message.text.split('.')[2]), int(message.text.split('.')[1]), int(message.text.split('.')[0]))
    await create_event(name, {'desc': desc, 'date': dat})
    # link = "https://t.me/?start={event.name}"
    await safe_send_message(bot, message, f"все круто, все создано!!\nсслыка для регистрации:"
                                          f"\nhttps://t.me/brewbegtbot?start={name}"
                                          f"ссылка для подтверждения:"
                                          f"\nhttps://t.me/brewbegtbot?start=reg_{name}")
    await state.clear()


class EventState(StatesGroup):
    waiting_ev = State()
    waiting_ev_for_link = State()


@router.message(Command("get_link"))
async def get_link(message: Message, state: FSMContext):
    events = await get_all_events_in_p()
    await safe_send_message(bot, message, text="Выберете событие", reply_markup=post_ev_tagret(events))
    await state.set_state(EventState.waiting_ev_for_link)


@router.message(EventState.waiting_ev_for_link)
async def make_link(message: Message, state: FSMContext):
    event = await get_event(message.text)
    # link = "https://t.me/?start={event.name}"
    await safe_send_message(bot, message, f"сслыка для регистрации:"
                                          f"\nhttps://t.me/brewbegtbot?start=reg_{event.name}"
                                          f"\nссылка для подтверждения:"
                                          f"\nhttps://t.me/brewbegtbot?start={event.name}")
    await state.clear()


@router.message(Command("end_event"))
async def cmd_end_event(message: Message, state: FSMContext):
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
    await safe_send_message(bot, callback, text=f"Предварительный победитель - @{user.handler}, проверьте его наличие в "
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
        await safe_send_message(bot, user_id, text=f"У вас нет пользоватеkей))", reply_markup=single_command_button_keyboard())
    else:
        for user_id in user_ids:
            await safe_send_message(bot, user_id, text=f"Сегодняшний победитель - @{user.handler}", reply_markup=single_command_button_keyboard())
    bad_user_ids = await get_users_tg_id_in_event_bad(event_name)
    if bad_user_ids:
        for user_id in bad_user_ids:
            await update_user_x_event_row_status(user_id, event_name, 'nbeen')
    await state.clear()


class VacancyState(StatesGroup):
    waiting_for_vacancy_name = State()
    waiting_for_vacancy_name_to_delete = State()


@router.message(Command("all_vacancies"))
async def cmd_all_vacancies(message: Message):
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
        await message.answer(f"Вакансия '{vacancy_name}' успешно добавлена.", reply_markup=single_command_button_keyboard())
        await state.clear()


@router.message(Command("dell_vacancy"))
async def cmd_dell_vacancy(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    vacancies = await get_all_vacancy_names()
    await safe_send_message(bot, message, text="Выберете название вакансии, которую вы хотите удалить", reply_markup=vacancy_selection_keyboard(vacancies))
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
    waiting_for_post_to_all_text = State()
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


@router.callback_query(F.data == "post_to_all")
async def cmd_post_to_all(callback: CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Отправьте мне пост")
    await state.set_state(PostState.waiting_for_post_to_all_text)


@router.message(PostState.waiting_for_post_to_all_text)
async def process_post_to_all(message: Message, state: FSMContext):
    user_ids = await get_users_tg_id()
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей((", reply_markup=single_command_button_keyboard())
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=message.text, reply_markup=single_command_button_keyboard())
    await safe_send_message(bot, message, "Готово", reply_markup=single_command_button_keyboard())
    await state.clear()


@router.callback_query(F.data == "post_to_ev")
async def cmd_post_to_ev(callback: CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(PostState.waiting_for_post_to_ev_ev)


@router.message(PostState.waiting_for_post_to_ev_ev)
async def pre_process_post_to_ev(message: Message, state: FSMContext):
    await safe_send_message(bot, message, text="Отправьте мне пост")
    await state.update_data(event_name=message.text)
    await state.set_state(PostState.waiting_for_post_to_ev_text)


@router.message(PostState.waiting_for_post_to_ev_text)
async def process_post_to_ev(message: Message, state: FSMContext):
    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей принявших участие в этом событии", reply_markup=single_command_button_keyboard())
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
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(PostState.waiting_for_post_wth_op_to_ev_ev)


@router.message(PostState.waiting_for_post_wth_op_to_ev_ev)
async def pre_process_post_to_ev(message: Message, state: FSMContext):
    await safe_send_message(bot, message, text="Отправьте мне ссылку на гугл-форму")
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
    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей принявших участие в этом событии", reply_markup=single_command_button_keyboard())
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=msg, reply_markup=feedback_form_ikb(message.text))
    await safe_send_message(bot, message, "Готово", reply_markup=single_command_button_keyboard())
    await state.clear()


class StatState(StatesGroup):
    waiting_for_ev = State()


@router.message(Command("send_stat"))
async def cmd_send_stat(message: Message):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Выберете какую статистику вы хотите получить", reply_markup=stat_target())


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
