"""
Questionnaire Router
Handlers for questionnaire FSM and callbacks.
"""

# --------------------------------------------------------------------------------
from aiogram import Router, F, types
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery

from bot_instance import bot
from database.req import (
    create_questionary,
    update_questionary,
    get_questionary,
    get_all_vacancy_names,
)
from handlers.error import safe_send_message
from keyboards.keyboards import (
    vacancy_selection_keyboard,
    another_vacancy_keyboard,
    quest_keyboard_1,
    quest_keyboard_2,
)

router = Router()

# --------------------------------------------------------------------------------

msg1 = """
HSE SPB Business Club — это открытое сообщество, которое объединяет талантливых студентов ВШЭ и успешных предпринимателей для обмена опытом и совместного развития.
    
Команда организаторов клуба обеспечивает всю операционную деятельность сообщества и разделена на 5 департаментов:
    
    - Marketing (продвижение всех мероприятий Клуба, взаимодействие с инфопартнерами Клуба)
    - Design (формирование единого дизайн-кода Клуба, разработка дизайн-материалов Клуба)
    - Event & Project (проведение мероприятий Клуба, обеспечение регулярных процессов Клуба)
    - SMM & Video production (ведение соцсетей Клуба, создание и управление всем контентом, фото и видеосъемка мероприятий Клуба)
    - HR (управление профессиональным и личностным развитием членов команды Клуба)
    
Отбор в команду организаторов разделен на 3 этапа. Проход на следующий этап возможен при успешном прохождении предыдущего. Ниже можно ознакомиться с ключевыми этапами отбора:
    
1. Заполнение информации о себе и своем опыте.
    
2. Прохождение группового/личного собеседования.
    
3. Тестовый период в команде Клуба: в течение проведения двух мероприятий.
    
Нажимай на кнопку ниже, присылай необходимую информацию и следи за новыми сообщениями!
"""

msg2 = """
Первый этап отбора — заполнение анкеты с информацией о себе и своем опыте.

На этом этапе сначала тебе будет предложено указать персональные данные. Затем ты сможешь выбрать интересующую(-ие) вакансию(-и). Далее тебя попросят ответить на содержательные вопросы о твоем опыте, твоей мотивации присоединиться к команде Клуба и другие важные вопросы.

Примерное время, необходимое для выполнения первого этапа отбора — 20-30 минут. Дедлайн приема заявок на первом этапе — 18 декабря 23:59.

О решении по своей заявке и дальнейших шагах в случае успешного прохождения этапов ты будешь оповещен(-а) через личные сообщения в Telegram.

В случае возникновения вопросов — пиши @vitaly_bshv
"""


# --------------------------------------------------------------------------------

class Questionnaire(StatesGroup):
    """
    State definitions for questionnaire process.
    """
    full_name = State()
    degree = State()
    course = State()
    program = State()
    email = State()
    vacancy = State()
    motivation = State()
    plans = State()
    strengths = State()
    career_goals = State()
    team_motivation = State()
    role_in_team = State()
    events = State()
    found_info = State()
    resume = State()
    another_vacancy = State()


# --------------------------------------------------------------------------------
@router.message(F.text == "Стать частью команды HSE SPB Business Club")
async def start2(message: types.Message):
    """
    Redirect text trigger to /quest command.

    Args:
        message (types.Message): Incoming message instance.
    """
    await start(message)


# --------------------------------------------------------------------------------
@router.message(Command("quest"))
async def start(message: types.Message):
    """
    Send introduction message and first keyboard.

    Args:
        message (types.Message): Incoming message instance.
    """
    await safe_send_message(
        bot,
        message,
        text=msg1,
        reply_markup=quest_keyboard_1(),
    )


# --------------------------------------------------------------------------------
@router.callback_query(F.data == "next")
async def start_2(callback: CallbackQuery):
    """
    Send details message and second keyboard on callback.

    Args:
        callback (CallbackQuery): Incoming callback query.
    """
    await safe_send_message(
        bot,
        callback,
        text=msg2,
        reply_markup=quest_keyboard_2(),
    )


# --------------------------------------------------------------------------------
async def start_nu(message: types.Message, state: FSMContext):
    """
    Initialize or continue questionnaire based on state.

    Args:
        message (types.Message): Incoming message or callback.
        state (FSMContext): FSM context instance.
    """
    vacancies = await get_all_vacancy_names()
    if not vacancies:
        await safe_send_message(
            bot, message,
            text="К сожалению сейчас нет доступных вакансий"
        )
        return
    quest = await get_questionary(message.from_user.id)
    if quest == "not created":
        await create_questionary(message.from_user.id)
    current = await state.get_state()
    second_states = [
        Questionnaire.motivation,
        Questionnaire.plans,
        Questionnaire.strengths,
        Questionnaire.career_goals,
        Questionnaire.team_motivation,
        Questionnaire.role_in_team,
        Questionnaire.events,
        Questionnaire.found_info,
        Questionnaire.resume,
        Questionnaire.another_vacancy,
    ]
    if current in second_states:
        await continue_from_second_part(message, state)
    else:
        await start_first_part(message, state)


# --------------------------------------------------------------------------------
async def start_first_part(message: types.Message, state: FSMContext):
    """
    Begin first part: request full name.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await safe_send_message(bot, message, text="Введите свое ФИО")
    await state.set_state(Questionnaire.full_name)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.full_name)
async def enter_full_name(message: types.Message, state: FSMContext):
    """
    Handle full name input and proceed to degree.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'full_name': message.text})
    await safe_send_message(bot, message, text="Введите свою степень обучения")
    await state.set_state(Questionnaire.degree)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.degree)
async def enter_degree(message: types.Message, state: FSMContext):
    """
    Handle degree input and proceed to course.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'degree': message.text})
    await safe_send_message(bot, message, text="Введите свой курс")
    await state.set_state(Questionnaire.course)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.course)
async def enter_course(message: types.Message, state: FSMContext):
    """
    Handle course input and proceed to program.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'course': message.text})
    await safe_send_message(bot, message, text="Напишите свою образовательную программу")
    await state.set_state(Questionnaire.program)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.program)
async def enter_program(message: types.Message, state: FSMContext):
    """
    Handle program input and proceed to email.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'program': message.text})
    await safe_send_message(bot, message, text="Введите свою электронную почту")
    await state.set_state(Questionnaire.email)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.email)
async def enter_email(message: types.Message, state: FSMContext):
    """
    Handle email input and request vacancy selection.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'email': message.text})
    vacancies = await get_all_vacancy_names()
    await safe_send_message(
        bot,
        message,
        text="Какая вакансия тебя интересует?",
        reply_markup=vacancy_selection_keyboard(vacancies),
    )
    await state.set_state(Questionnaire.vacancy)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.vacancy)
async def enter_vacancy(message: types.Message, state: FSMContext):
    """
    Handle vacancy selection and ask for another.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'vacancy': message.text})
    await safe_send_message(
        bot,
        message,
        text="Хочешь подать заявку на другую вакансию?",
        reply_markup=another_vacancy_keyboard(),
    )
    await state.set_state(Questionnaire.another_vacancy)


# --------------------------------------------------------------------------------
@router.callback_query(StateFilter(Questionnaire.another_vacancy), F.data.startswith("another_"))
async def ask_another_vacancy(callback: CallbackQuery, state: FSMContext):
    """
    Handle another vacancy choice or continue questionnaire.

    Args:
        callback (CallbackQuery): Incoming callback query.
        state (FSMContext): FSM context instance.
    """
    if callback.data == "another_yes":
        vacancies = await get_all_vacancy_names()
        await callback.message.edit_text(
            "Какая вакансия тебя интересует?",
            reply_markup=vacancy_selection_keyboard(vacancies),
        )
        await state.set_state(Questionnaire.vacancy)
    else:
        await callback.message.edit_text("Спасибо за ваш выбор.")
        await continue_from_second_part(callback.message, state)
    await callback.answer()


# --------------------------------------------------------------------------------
async def continue_from_second_part(message: types.Message, state: FSMContext):
    """
    Begin second part: ask motivation.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await safe_send_message(bot, message, text="Мотивация стать частью HSE Business Club")
    await state.set_state(Questionnaire.motivation)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.motivation)
async def enter_motivation(message: types.Message, state: FSMContext):
    """
    Handle motivation input and proceed to plans.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'motivation': message.text})
    await safe_send_message(bot, message, text="Какие у тебя планы на этот учебный год?")
    await state.set_state(Questionnaire.plans)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.plans)
async def enter_plans(message: types.Message, state: FSMContext):
    """
    Handle plans input and proceed to strengths.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.
    """
    await update_questionary(message.from_user.id, {'plans': message.text})
    await safe_send_message(bot, message, text="Какие твои сильные качества?")
    await state.set_state(Questionnaire.strengths)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.strengths)
async def enter_strengths(message: types.Message, state: FSMContext):
    """
    Handle strengths input and proceed to career goals.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'strengths': message.text})
    await safe_send_message(bot, message, text="Как ты видишь для себя развитие своей карьеры?")
    await state.set_state(Questionnaire.career_goals)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.career_goals)
async def enter_career_goals(message: types.Message, state: FSMContext):
    """
    Handle career goals input and proceed to team motivation.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'career_goals': message.text})
    await safe_send_message(bot, message, text="Почему ты хочешь попасть к нам в команду?")
    await state.set_state(Questionnaire.team_motivation)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.team_motivation)
async def enter_team_motivation(message: types.Message, state: FSMContext):
    """
    Handle team motivation input and proceed to role in team.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'team_motivation': message.text})
    await safe_send_message(bot, message, text="В какой роли ты видишь себя в команде?")
    await state.set_state(Questionnaire.role_in_team)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.role_in_team)
async def enter_role_in_team(message: types.Message, state: FSMContext):
    """
    Handle role in team input and proceed to events.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'role_in_team': message.text})
    await safe_send_message(bot, message, text="На каких мероприятиях Бизнес-клуба ты был(-а)?")
    await state.set_state(Questionnaire.events)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.events)
async def enter_events(message: types.Message, state: FSMContext):
    """
    Handle events input and proceed to found info.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'events': message.text})
    await safe_send_message(bot, message, text="Где ты узнал(-а) про отбор в Бизнес-клуб?")
    await state.set_state(Questionnaire.found_info)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.found_info)
async def enter_found_info(message: types.Message, state: FSMContext):
    """
    Handle found info input and proceed to resume.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'found_info': message.text})
    await safe_send_message(bot, message, text="Отправь ссылку на свое резюме/портфолио")
    await state.set_state(Questionnaire.resume)


# --------------------------------------------------------------------------------
@router.message(Questionnaire.resume)
async def enter_resume(message: types.Message, state: FSMContext):
    """
    Handle resume input and end questionnaire.

    Args:
        message (types.Message): Incoming message instance.
        state (FSMContext): FSM context instance.

    Returns:
        None
    """
    await update_questionary(message.from_user.id, {'resume': message.text})
    await safe_send_message(bot, message, text="Благодарим тебя за заполнение анкеты!")
    await state.clear()
