from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from error import safe_send_message
from bot_instance import bot
from database.req import get_user, create_user, add_vacancy, delete_vacancy, get_users_tg_id, get_all_events,  get_users_tg_id_in_event
from keyboards.keyboards import post_target, post_ev_tagret, stat_target


router = Router()


@router.message(Command("add_event"))
async def cmd_add_event():
    pass


async def cmd_end_event():
    pass


class VacancyState(StatesGroup):
    waiting_for_vacancy_name = State()
    waiting_for_vacancy_name_to_delete = State()


@router.message(Command("add_vacancy"))
async def cmd_add_vacancy(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Введите название вакансии")
    await state.set_state(VacancyState.waiting_for_vacancy_name)


@router.message(VacancyState.waiting_for_vacancy_name)
async def process_vacancy_name(message: Message, state: FSMContext):
    vacancy_name = message.text
    await add_vacancy(vacancy_name)
    await message.answer(f"Вакансия '{vacancy_name}' успешно добавлена.")
    await state.clear()


@router.message(Command("dell_vacancy"))
async def cmd_dell_vacancy(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Введите название вакансии, которую вы хотите удалить")
    await state.set_state(VacancyState.waiting_for_vacancy_name_to_delete)


@router.message(VacancyState.waiting_for_vacancy_name_to_delete)
async def process_vacancy_name_to_delete(message: Message, state: FSMContext):
    vacancy_name = message.text
    await delete_vacancy(vacancy_name)
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


@router.callback_query(F.data == "post_to_env")
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
    await safe_send_message(bot, callback, text="Да, конечно, вот:")
    # TODO: create stat about all and send(view in cb)


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
    await safe_send_message(bot, message, text="Да, конечно, вот:")
    # TODO: create stat about ev and send (view in cb)
    await state.clear()


