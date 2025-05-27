"""
Vacancy Management
Handles creation, viewing and deletion of vacancies.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.settings import TOKEN
from database.req import (
    get_user, get_all_vacancy_names, add_vacancy, delete_vacancy
)
from handlers.error import safe_send_message
from handlers.states import VacancyState
from keyboards import main_reply_keyboard, vacancy_selection_keyboard

# --------------------------------------------------------------------------------

router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# --------------------------------------------------------------------------------

@router.message(Command("all_vacancies"))
async def cmd_all_vacancies(message: Message):
    """
    Sends a list of all active vacancies to the admin.

    Args:
        message (Message): Incoming command message.

    Returns:
        None
    """
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
    await safe_send_message(
        bot,
        message,
        text=msg,
        reply_markup=main_reply_keyboard()
    )


# --------------------------------------------------------------------------------

@router.message(Command("add_vacancy"))
async def cmd_add_vacancy(message: Message, state: FSMContext):
    """
    Starts the process of adding a new vacancy.

    Args:
        message (Message): Incoming command message.
        state (FSMContext): FSM context to track input.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(bot, message, text="Введите название вакансии")
    await state.set_state(VacancyState.waiting_for_vacancy_name)


# --------------------------------------------------------------------------------

@router.message(VacancyState.waiting_for_vacancy_name)
async def process_vacancy_name(message: Message, state: FSMContext):
    """
    Saves the new vacancy or handles duplicates.

    Args:
        message (Message): Message with vacancy name.
        state (FSMContext): FSM context for state cleanup.

    Returns:
        None
    """
    if message.text.lower() == "стоп":
        await state.clear()
        return
    vacancy_name = message.text
    resp = await add_vacancy(vacancy_name)
    if not resp:
        await message.answer(
            f"Вакансия с именем '{vacancy_name}' уже существует.\n"
            f"Если хотите добавить другую - напишите ее название.\n"
            f"Если не хотите напишите \"стоп\""
        )
    else:
        await message.answer(
            f"Вакансия '{vacancy_name}' успешно добавлена.",
            reply_markup=main_reply_keyboard()
        )
        await state.clear()


# --------------------------------------------------------------------------------

@router.message(Command("dell_vacancy"))
async def cmd_dell_vacancy(message: Message, state: FSMContext):
    """
    Starts the process to delete a vacancy.

    Args:
        message (Message): Incoming command message.
        state (FSMContext): FSM context to store deletion state.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    vacancies = await get_all_vacancy_names()
    await safe_send_message(
        bot,
        message,
        text="Выберете название вакансии, которую вы хотите удалить",
        reply_markup=vacancy_selection_keyboard(vacancies)
    )
    await state.set_state(VacancyState.waiting_for_vacancy_name_to_delete)


# --------------------------------------------------------------------------------

@router.message(VacancyState.waiting_for_vacancy_name_to_delete)
async def process_vacancy_name_to_delete(message: Message, state: FSMContext):
    """
    Deletes the specified vacancy.

    Args:
        message (Message): Message with the vacancy name.
        state (FSMContext): FSM context for cleanup.

    Returns:
        None
    """
    vacancy_name = message.text
    resp = await delete_vacancy(vacancy_name)
    if not resp:
        await message.answer(
            f"Вакансии '{vacancy_name}' нет.",
            reply_markup=main_reply_keyboard()
        )
        await state.clear()
        return

    await message.answer(
        f"Вакансия '{vacancy_name}' успешно удалена.",
        reply_markup=main_reply_keyboard()
    )
    await state.clear()
