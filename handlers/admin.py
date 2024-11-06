from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from handlers.error import safe_send_message
from bot_instance import bot
from database.req import (get_user, create_user, add_vacancy, delete_vacancy, get_users_tg_id, get_all_events,
                          get_users_tg_id_in_event, get_random_user_from_event, update_event,
                          get_random_user_from_event_wth_bad, get_all_vacancy_names, get_event, get_all_events_in_p)
from keyboards.keyboards import post_target, post_ev_tagret, stat_target, apply_winner, vacancy_selection_keyboard
from statistics.stat import get_stat_all, get_stat_all_in_ev, get_stat_quest


router = Router()


class EventState(StatesGroup):
    waiting_ev = State()


async def get_link():
    pass

#https://t.me/brewbegtbot?start=ff


@router.message(Command("add_event"))
async def cmd_add_event():
    pass


@router.message(Command("end_event"))
async def cmd_end_event(message: Message, state: FSMContext):
    events = await get_all_events_in_p()
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
async def reroll_end_event(callback: F.CallbackQuery, state: FSMContext):
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
async def confirm_end_event(callback: F.CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Отличное, рассылаю все информацию")
    data = await state.get_data()
    event_name = data.get("event_name")
    user_id = data.get("user_id")
    await update_event(event_name, {'winner': user_id, "status": "end"})
    user = await get_user(user_id)
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, user_id, text=f"У вас нет пользоватеkей))")
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=f"Сегодняшний победитель - @{user.handler}")
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
    await safe_send_message(bot, message, text=msg)


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
        await message.answer(f"Вакансия '{vacancy_name}' успешно добавлена.")
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
        await message.answer(f"Вакансии '{vacancy_name}' нет.")
        await state.clear()
    await message.answer(f"Вакансия '{vacancy_name}' успешно удалена.")
    await state.clear()


class PostState(StatesGroup):
    waiting_for_post_to_all_text = State()
    waiting_for_post_to_ev_ev = State()
    waiting_for_post_to_ev_text = State()


@router.message(Command("send_post"))
async def cmd_send_post(message: Message):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Выберете кому вы хотите отправить пост", reply_markup=post_target())


@router.callback_query(F.data == "post_to_all")
async def cmd_post_to_all(callback: F.CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Отправьте мне пост")
    await state.set_state(PostState.waiting_for_post_to_all_text)


@router.message(PostState.waiting_for_post_to_all_text)
async def process_post_to_all(message: Message, state: FSMContext):
    user_ids = await get_users_tg_id()
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей((")
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=message.text)
    await state.clear()


@router.callback_query(F.data == "post_to_ev")
async def cmd_post_to_ev(callback: F.CallbackQuery, state: FSMContext):
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


@router.message(PostState.waiting_for_post_to_all_text)
async def process_post_to_all(message: Message, state: FSMContext):
    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(bot, message, text="У вас нет пользователей принявших участие в этом событии")
        return
    for user_id in user_ids:
        await safe_send_message(bot, user_id, text=message.text)
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
async def cmd_stat_all(callback: F.CallbackQuery):
    await get_stat_all(callback.from_user.id)


@router.callback_query(F.data == "stat_ev")
async def cmd_stat_ev(callback: F.CallbackQuery, state: FSMContext):
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(bot, callback, text="Выберете событие:", reply_markup=post_ev_tagret(events))
    await state.set_state(StatState.waiting_for_ev)


@router.message(StatState.waiting_for_ev)
async def process_post_to_all(message: Message, state: FSMContext):
    await get_stat_all_in_ev(message.from_user.id, message.text)
    await state.clear()


@router.callback_query(F.data == "stat_quest")
async def cmd_stat_ev(callback: F.CallbackQuery):
    await get_stat_quest(callback.from_user.id)
