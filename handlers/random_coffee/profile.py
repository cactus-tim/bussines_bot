"""
Random Coffee Profile

Handlers for creating and updating user profiles for Random Coffee.
"""

# --------------------------------------------------------------------------------

import logging
from datetime import datetime

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import TOKEN
from database.models import RandomCoffeeProfile, RandomCoffeeWeek
from database.req.random_coffee import get_user_profile
from handlers.states import ProfileStates
from keyboards.random_coffee.base import (
    get_city_keyboard,
    get_meeting_goal_keyboard,
    get_meeting_format_keyboard,
    get_profile_edit_keyboard,
    get_weekly_participation_keyboard,
    cancel_weekly_participation_keyboard
)
from utils.random_coffee.helpers import (
    get_profile_text,
    validate_birth_date,
    get_week_start_date
)

# --------------------------------------------------------------------------------

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)

router = Router()
logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------------

@router.message(Command("random_coffee"))
@router.message(F.text == "☕ Участвовать в Random Coffee")
async def cmd_random_coffee(message: Message, state: FSMContext, session: AsyncSession):
    """
    Handle the /random_coffee command and manage user participation.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context for the user.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        profile = await get_user_profile(session, message.from_user.id)

        if profile:
            current_week = get_week_start_date()
            existing_participation = await session.scalar(
                select(RandomCoffeeWeek).where(
                    RandomCoffeeWeek.user_id == message.from_user.id,
                    RandomCoffeeWeek.week_start == current_week.isoformat(),
                )
            )

            if existing_participation:
                if existing_participation.is_participating:
                    await message.answer(
                        "Вы уже зарегистрированы на участие в Random Coffee на этой неделе.",
                        reply_markup=cancel_weekly_participation_keyboard()
                    )
                    return
                else:
                    await message.answer(
                        text="Вы хотите участвовать в Random Coffee на следующей неделе?",
                        reply_markup=get_weekly_participation_keyboard()
                    )
            else:
                await message.answer(
                    text="Вы хотите участвовать в Random Coffee на следующей неделе?",
                    reply_markup=get_weekly_participation_keyboard()
                )
        else:
            await message.answer(
                "Скоро рассылка пар.\n"
                "Чтобы присоединиться ко встречам, ответь на вопрос бота выше и заверши анкету."
            )
            await message.answer(
                "Вопрос 1 из 7.\n"
                "☕️ <b>Как тебя зовут?</b> Напиши имя и фамилию."
            )
            await state.set_state(ProfileStates.waiting_for_full_name)

    except Exception as e:
        logger.error(f"Error in cmd_random_coffee: {e}")
        await message.answer(
            "Произошла ошибка при создании анкеты. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )


# --------------------------------------------------------------------------------

async def update_user(
        message: Message | CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        key,
        value
):
    """
    Update a specific field in the user's profile.

    Args:
        message (Message | CallbackQuery): Incoming Telegram message.
        session (AsyncSession): Database session.
        state (FSMContext): FSM state context.
        key (str): Profile field name.
        value (str): New value for the field.

    Returns:
        None
    """
    profile = await get_user_profile(session, message.from_user.id)
    setattr(profile, key, value)
    await session.commit()

    await message.answer("✅ Изменение сохранено!")
    await state.clear()


# --------------------------------------------------------------------------------

@router.message(ProfileStates.waiting_for_full_name)
async def process_full_name(message: Message, state: FSMContext, session: AsyncSession):
    """
    Process full name input and advance to city question.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(message, session, state, "full_name", message.text)
            return

        await state.update_data(full_name=message.text)
        await message.answer(
            "Вопрос 2 из 7.\n"
            "📍 <b>Из какого ты города?</b> Выбери или напиши в ответ.\n\n"
            "Вы с партнером можете оказаться в разных городах - тогда вам подойдет "
            "онлайн-формат встречи. А если вы из одного города, сможете встретиться вживую!",
            reply_markup=get_city_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_city)

    except Exception as e:
        logger.error(f"Error in process_full_name: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("city_"))
async def process_city(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Process selected city or ask for custom input.

    Args:
        callback (CallbackQuery): Callback from inline button.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        city_type = callback.data.split("_")[1]

        if city_type == "other":
            await callback.message.answer(
                "Пожалуйста, введите название вашего города:"
            )
            await state.set_state(ProfileStates.waiting_for_custom_city)
        else:
            city_map = {'spb': 'Санкт-Петербург', 'moscow': 'Москва'}
            city = city_map.get(city_type, city_type)
            data = await state.get_data()
            if data.get("editing_profile"):
                await update_user(callback, session, state, "city", city)
                return

            await state.update_data(city=city)
            await callback.message.answer(
                "Вопрос 3 из 7.\n"
                "👨‍💻 Пришли ссылку на <b>профиль в соц. сетях</b>, который активно ведешь.\n\n"
                "Можно оставить ссылку на конкретный пост о себе или даже интервью - "
                "что-то, что поможет человеку заочно познакомиться с тобой до первой встречи."
            )
            await state.set_state(ProfileStates.waiting_for_social)

        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_city: {e}")
        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.message(ProfileStates.waiting_for_custom_city)
async def process_custom_city(message: Message, state: FSMContext, session: AsyncSession):
    """
    Handle custom city input from user.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(message, session, state, "city", message.text)
            return

        await state.update_data(city=message.text)
        await message.answer(
            "Вопрос 3 из 7.\n"
            "👨‍💻 Пришли ссылку на <b>профиль в соц. сетях</b>, который активно ведешь.\n\n"
            "Можно оставить ссылку на конкретный пост о себе или даже интервью - "
            "что-то, что поможет человеку заочно познакомиться с тобой до первой встречи."
        )
        await state.set_state(ProfileStates.waiting_for_social)
    except Exception as e:
        logger.error(f"Error in process_custom_city: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.message(ProfileStates.waiting_for_social)
async def process_social(message: Message, state: FSMContext, session: AsyncSession):
    """
    Save user's social link and ask for occupation.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(message, session, state, "social_links", message.text)
            return

        await state.update_data(social_links=message.text)
        await message.answer(
            "Вопрос 4 из 7.\n"
            "👨‍💻 <b>Коротко расскажи чем занимается твоя компания.</b>"
        )
        await state.set_state(ProfileStates.waiting_for_occupation)
    except Exception as e:
        logger.error(f"Error in process_social: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.message(ProfileStates.waiting_for_occupation)
async def process_occupation(message: Message, state: FSMContext, session: AsyncSession):
    """
    Save user's occupation and ask for hobbies.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(message, session, state, "occupation", message.text)
            return

        await state.update_data(occupation=message.text)
        await message.answer(
            "Вопрос 5 из 7.\n"
            "👀 <b>Какое у тебя хобби?</b>"
        )
        await state.set_state(ProfileStates.waiting_for_hobbies)
    except Exception as e:
        logger.error(f"Error in process_occupation: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.message(ProfileStates.waiting_for_hobbies)
async def process_hobbies(message: Message, state: FSMContext, session: AsyncSession):
    """
    Save user's hobbies and ask for birth date.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(message, session, state, "hobbies", message.text)
            return

        await state.update_data(hobbies=message.text)
        await message.answer(
            "Вопрос 6 из 7.\n"
            "📆 <b>Напиши дату рождения в формате дд.мм.гггг.</b>"
        )
        await state.set_state(ProfileStates.waiting_for_birth_date)
    except Exception as e:
        logger.error(f"Error in process_hobbies: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.message(ProfileStates.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext, session: AsyncSession):
    """
    Validate and save birth date, then ask for meeting goal.

    Args:
        message (Message): Incoming Telegram message.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        if not validate_birth_date(message.text):
            await message.answer(
                "Неверный формат даты.\nПожалуйста, используйте формат ДД.ММ.ГГГГ:"
            )
            return

        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(message, session, state, "birth_date", message.text)
            return

        await state.update_data(birth_date=message.text)
        await message.answer(
            "Вопрос 7 из 7.\n"
            "⚖️ Некоторые люди приходят на Random Coffee встречи, чтобы найти партнеров "
            "для будущих проектов и завести полезные контакты, условно назовем это "
            "<b>пользой</b>. А кто-то приходит для расширения кругозора, новых эмоций и "
            "открытия чего-то нового, назовем это <b>фан</b>. "
            "<b>Какое описание больше подходит тебе?</b>",
            reply_markup=get_meeting_goal_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_goal)
    except Exception as e:
        logger.error(f"Error in process_birth_date: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("goal_"))
async def process_goal(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Process user-selected meeting goal and proceed to format selection.

    Args:
        callback (CallbackQuery): Callback from inline button.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        goal_map = {
            "10-90": "10% фан / 90% польза",
            "30-70": "30% фан / 70% польза",
            "50-50": "50% фан / 50% польза",
            "70-30": "70% фан / 30% польза",
            "90-10": "90% фан / 10% польза"
        }

        goal = goal_map[callback.data.split("_")[1]]

        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(callback, session, state, "meeting_goal", goal)
            return

        await state.update_data(meeting_goal=goal)
        await callback.message.answer(
            "☕ На случай, если бот не успеет дополнительно уточнить перед первой встречей, "
            "отметь ниже, в каком формате хочешь ее провести: вживую или онлайн?\n\n"
            "Если выберешь \"вживую\", бот постарается подобрать собеседника из твоего города, "
            "который тоже хочет встретиться оффлайн, и пришлёт рандомную пару только если не "
            "удастся найти подходящего партнёра.",
            reply_markup=get_meeting_format_keyboard()
        )
        await state.set_state(ProfileStates.waiting_for_format)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_goal: {e}")
        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("format_"))
async def process_format(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    """
    Save selected meeting format and finalize profile creation.

    Args:
        callback (CallbackQuery): Callback from inline button.
        state (FSMContext): FSM state context.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        format_map = {
            "online": "Онлайн",
            "offline": "Вживую"
        }
        format_type = format_map[callback.data.split("_")[1]]

        data = await state.get_data()
        if data.get("editing_profile"):
            await update_user(callback, session, state, "meeting_format", format_type)
            return

        data["meeting_format"] = format_type

        profile = RandomCoffeeProfile(
            user_id=callback.from_user.id,
            **data
        )
        session.add(profile)

        week_start = get_week_start_date()
        participation = RandomCoffeeWeek(
            user_id=callback.from_user.id,
            week_start=week_start.isoformat(),
            is_participating=True,
            created_at=datetime.now().isoformat()
        )
        session.add(participation)

        await session.commit()

        await callback.message.answer(
            "<b>Получилось!</b>🤲\n\n"
            "Теперь ты - участник встреч Random Coffee☕\n\n"
            "Вот так будет выглядеть твой профиль в сообщении, которое мы перешлем твоему собеседнику:\n⏬"
        )
        await callback.message.answer(
            get_profile_text(profile) + "\n\nЕсли нужно что-то поменять, используйте команду /edit_profile"
        )
        await callback.message.answer("Хороших встреч! ☕️")
        await state.clear()
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_format: {e}")
        await callback.message.answer(
            "Произошла ошибка при сохранении анкеты. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )


# --------------------------------------------------------------------------------

@router.message(Command("edit_profile"))
async def cmd_edit_profile(message: Message, session: AsyncSession):
    """
    Handle /edit_profile command and display editable profile data.

    Args:
        message (Message): Incoming Telegram message.
        session (AsyncSession): Database session.

    Returns:
        None
    """
    try:
        profile = await get_user_profile(session, message.from_user.id)

        if not profile:
            await message.answer(
                "У вас еще нет анкеты Random Coffee. "
                "Используйте /random_coffee для создания анкеты."
            )
            return

        text = (
                get_profile_text(profile)
                + "\n----------------\n"
                + f"<b>Дата рождения:</b> {profile.birth_date}\n"
                + f"<b>Формат встречи:</b> {profile.meeting_format}\n\n"
                + "Выберите, что хотите изменить:"
        )

        await message.answer(
            text,
            reply_markup=get_profile_edit_keyboard()
        )
    except Exception as e:
        logger.error(f"Error in cmd_edit_profile: {e}")
        await message.answer(
            "Произошла ошибка при просмотре анкеты. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("edit_"))
async def process_profile_edit(callback: CallbackQuery, state: FSMContext):
    """
    Process profile edit command and set appropriate state.

    Args:
        callback (CallbackQuery): Callback from inline button.
        state (FSMContext): FSM state context.

    Returns:
        None
    """
    try:
        field = callback.data.split("_")[1]
        await state.update_data(editing_profile=True)

        if field == "fullname":
            await callback.message.answer("Введите новое ФИО:")
            await state.set_state(ProfileStates.waiting_for_full_name)
        elif field == "city":
            await callback.message.answer(
                "Выберите новый город:",
                reply_markup=get_city_keyboard()
            )
            await state.set_state(ProfileStates.waiting_for_city)
        elif field == "social":
            await callback.message.answer("Введите новые ссылки на социальные сети:")
            await state.set_state(ProfileStates.waiting_for_social)
        elif field == "occupation":
            await callback.message.answer("Введите новый род деятельности:")
            await state.set_state(ProfileStates.waiting_for_occupation)
        elif field == "hobbies":
            await callback.message.answer("Введите новые хобби:")
            await state.set_state(ProfileStates.waiting_for_hobbies)
        elif field == "birth_date":
            await callback.message.answer(
                "Введите новую дату рождения в формате ДД.ММ.ГГГГ:"
            )
            await state.set_state(ProfileStates.waiting_for_birth_date)
        elif field == "goal":
            await callback.message.answer(
                "Выберите новую цель знакомства:",
                reply_markup=get_meeting_goal_keyboard()
            )
            await state.set_state(ProfileStates.waiting_for_goal)
        elif field == "format":
            await callback.message.answer(
                "Выберите новый формат встреч:",
                reply_markup=get_meeting_format_keyboard()
            )
            await state.set_state(ProfileStates.waiting_for_format)

        await callback.answer()
    except Exception as e:
        logger.error(f"Error in process_profile_edit: {e}")
        await callback.message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте еще раз."
        )
