"""
Start command handler
Handles /start command and hash-based user scenarios.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from database.req import (
    get_user, create_user_x_event_row, get_event,
    update_user_x_event_row_status, update_reg_event, check_completly_reg_event,
    create_reg_event, get_reg_event, get_user_x_event_row, get_ref_give_away,
    create_ref_give_away, delete_user_x_event_row, delete_ref_give_away_row,
    get_all_hosts_in_event_ids, get_host, add_money, one_more_event,
    add_referal_cnt, update_strick, add_user_to_networking
)
from handlers.error import safe_send_message
from handlers.public.club_events.qr import send_event_qr_code
from handlers.public.quest import start
from handlers.public.utils.base import create_user_if_not_exists
from handlers.states import EventReg
from keyboards import (
    main_reply_keyboard, yes_no_ikb, yes_no_hse_ikb, get_ref_ikb
)

# --------------------------------------------------------------------------------

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# --------------------------------------------------------------------------------


async def handle_networking_hash(user_id: int, username: str, message: Message):
    """
    Handle the networking registration hash.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        message (Message): Incoming message object.

    Returns:
        None
    """
    await create_user_if_not_exists(user_id, username, 'networking')
    flag = await add_user_to_networking(user_id)
    if not flag:
        await safe_send_message(bot, user_id, 'Вы уже участвуете в нетворкинге')
    else:
        await safe_send_message(bot, user_id, 'Поздравляем! Вы участвуете в нетворкинге')
    await bot.delete_message(user_id, message.message_id - 1)


async def handle_reg_hash(user_id: int, username: str, hash_value: str, message: Message, state: FSMContext):
    """
    Handle registration hash for event sign-up.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        hash_value (str): Registration hash string.
        message (Message): Incoming message object.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await create_user_if_not_exists(user_id, username, hash_value[4:])
    event_name = '_'.join(hash_value.split('_')[1:4])
    user_x_event = await get_user_x_event_row(user_id, event_name)
    if user_x_event == 'not created':
        await create_user_x_event_row(user_id, event_name, hash_value.split('_')[-1])
        event = await get_event(event_name)
        if event == 'not created':
            await safe_send_message(bot, message, 'Такого события не существует..')
        await state.update_data({'name': event_name})
        await safe_send_message(
            bot, message,
            f'Хотите зарегистрироваться на мероприятие "{event.desc}", которое пройдет '
            f'{event.date} в {event.time}',
            reply_markup=yes_no_ikb()
        )
    else:
        await safe_send_message(
            bot, message,
            'Вы уже зарегистрировались на это мероприятие',
            reply_markup=get_ref_ikb(event_name)
        )


async def handle_ref_hash(user_id: int, username: str, hash_value: str, message: Message, state: FSMContext):
    """
    Handle referral hash and event registration.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        hash_value (str): Referral hash string.
        message (Message): Incoming message object.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    event_part, ref_user_id = hash_value.split("__")
    event_name = event_part.replace("ref_", "")
    ref_user_id = int(ref_user_id)

    await create_user_if_not_exists(user_id, username, str(ref_user_id))
    user_x_event = await get_user_x_event_row(user_id, event_name)
    if user_x_event == 'not created':
        await create_user_x_event_row(user_id, event_name, str(ref_user_id))
        event = await get_event(event_name)
        if event == 'not created':
            await safe_send_message(bot, message, 'Такого события не существует..')
        await state.update_data({'name': event_name})
        await safe_send_message(
            bot, message,
            f'Хотите зарегистрироваться на мероприятие "{event.desc}", которое пройдет '
            f'{event.date} в {event.time}',
            reply_markup=yes_no_ikb()
        )
        hosts_ids = await get_all_hosts_in_event_ids(event_name)
        if hosts_ids and ref_user_id in hosts_ids:
            ref_give_away = await get_ref_give_away(user_id, event_name)
            if not ref_give_away:
                await create_ref_give_away(user_id, event_name, ref_user_id)
                host = await get_host(ref_user_id, event_name)
                await safe_send_message(
                    bot, message,
                    f'Поздравляю, вы участвуете в розыгрыше, предназначенным только для подписчиков '
                    f'@{host.org_name}'
                )
            else:
                await safe_send_message(bot, message, 'Вы уже участвуете в чьем то розыгрыше')
        await safe_send_message(
            bot, ref_user_id,
            f"По твоей реферальной ссылке зарегистрировался на событие пользователь @{username}!"
        )
    else:
        await safe_send_message(
            bot, message,
            'Вы уже зарегистрировались на это мероприятие',
            reply_markup=get_ref_ikb(event_name)
        )


async def handle_otbor_hash(user_id: int, username: str, message: Message):
    """
    Handle 'otbor' hash.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        message (Message): Incoming message object.

    Returns:
        None
    """
    await create_user_if_not_exists(user_id, username, 'otbor')
    name = message.from_user.first_name if message.from_user.first_name else username
    await safe_send_message(bot, message, f'Привет, {name}!', reply_markup=main_reply_keyboard())
    await start(message)


async def handle_default_hash(user_id: int, username: str, hash_value: str, message: Message):
    """
    Handle unknown/default hash behavior.

    Args:
        user_id (int): Telegram user ID.
        username (str): Telegram username.
        hash_value (str): Default hash string.
        message (Message): Incoming message object.

    Returns:
        None
    """
    user = await create_user_if_not_exists(user_id, username, hash_value)

    row = await update_user_x_event_row_status(user_id, hash_value, 'been')
    if not row:
        await create_user_x_event_row(user_id, hash_value, '0')
        row = await update_user_x_event_row_status(user_id, hash_value, 'been')

    await add_money(user_id, 1)
    await one_more_event(user_id)
    await update_strick(user_id)

    ref_giver = await get_user(int(row.first_contact))

    await safe_send_message(
        bot, message,
        text="QR-код удачно отсканирован!",
        reply_markup=main_reply_keyboard()
    )

    hosts_ids = await get_all_hosts_in_event_ids(hash_value)
    if (not hosts_ids and ref_giver != 'not created') or (
            hosts_ids and ref_giver != 'not created' and ref_giver.id not in hosts_ids
    ):
        await safe_send_message(
            bot, ref_giver.id,
            f'Вы получили 2 монетки за то что приглашенный вами человек @{user.handler} '
            f'посетил событие!'
        )
        await add_money(ref_giver.id, 2)
        await add_referal_cnt(ref_giver.id)
        await safe_send_message(
            bot, user_id,
            f'Вы получили монетку за то что вы зарегистрировались по реферальной ссылке '
            f'@{ref_giver.handler}!'
        )
        await add_money(user_id, 1)


@router.callback_query(F.data == "event_no")
async def reg_event_part0_5(callback: CallbackQuery, state: FSMContext):
    """
    Handle user declining event registration.

    Args:
        callback (CallbackQuery): Callback query from Telegram.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await safe_send_message(bot, callback, "Это очень грустно((",
                            reply_markup=main_reply_keyboard())
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
    """
    Ask user if they are an HSE student/employee.

    Args:
        callback (CallbackQuery): Callback query from Telegram.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await safe_send_message(bot, callback, "Вы студент/сотрудник НИУ ВШЭ?",
                            reply_markup=yes_no_hse_ikb())


@router.callback_query(F.data == "hse_yes")
async def reg_event_part1_5(callback: CallbackQuery, state: FSMContext):
    """
    Process HSE student/employee event QR code.

    Args:
        callback (CallbackQuery): Callback query from Telegram.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    data = await state.get_data()
    name = data.get('name')
    await send_event_qr_code(callback.from_user.id, name, callback, state)


@router.callback_query(F.data == "hse_no")
async def reg_event_part2(callback: CallbackQuery, state: FSMContext):
    """
    Handle registration for non-HSE users.

    Args:
        callback (CallbackQuery): Callback query from Telegram.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    reg_event = await get_reg_event(callback.from_user.id)
    if not reg_event:
        await create_reg_event(callback.from_user.id)
        flag = False
    else:
        flag = await check_completly_reg_event(callback.from_user.id)

    if flag:
        data = await state.get_data()
        name = data.get('name')
        await send_event_qr_code(callback.from_user.id, name, callback, state)
    else:
        await safe_send_message(
            bot, callback,
            "Для пропуска на мероприятие нужно будет сообщить ваши данные. "
            "Напишите, пожалуйста, ваше имя"
        )
        await state.set_state(EventReg.waiting_name)


# --------------------------------------------------------------------------------


@router.message(EventReg.waiting_name)
async def reg_event_part3(message: Message, state: FSMContext):
    """
    Store user name and ask for surname.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await update_reg_event(message.from_user.id, {'name': message.text})
    await safe_send_message(bot, message, 'Напишите, пожалуйста, вашу фамилию')
    await state.set_state(EventReg.waiting_surname)


@router.message(EventReg.waiting_surname)
async def reg_event_part4(message: Message, state: FSMContext):
    """
    Store user surname and ask for fathername.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await update_reg_event(message.from_user.id, {'surname': message.text})
    await safe_send_message(bot, message, 'Напишите, пожалуйста, ваше отчество')
    await state.set_state(EventReg.waiting_fathername)


@router.message(EventReg.waiting_fathername)
async def reg_event_part5(message: Message, state: FSMContext):
    """
    Store user fathername and ask for phone.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await update_reg_event(message.from_user.id, {'fathername': message.text})
    await safe_send_message(bot, message, 'Укажите, пожалуйста, ваш мобильный телефон')
    await state.set_state(EventReg.waiting_phone)


@router.message(EventReg.waiting_phone)
async def reg_event_part6(message: Message, state: FSMContext):
    """
    Store user phone and ask for email.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await update_reg_event(message.from_user.id, {'phone': message.text})
    await safe_send_message(bot, message, 'Укажите, пожалуйста, вашу почту')
    await state.set_state(EventReg.waiting_mail)


@router.message(EventReg.waiting_mail)
async def reg_event_part7(message: Message, state: FSMContext):
    """
    Store user email and ask for organization.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await update_reg_event(message.from_user.id, {'mail': message.text})
    await safe_send_message(bot, message, 'Укажите, пожалуйста, из какого вы вуза/организации')
    await state.set_state(EventReg.waiting_org)


@router.message(EventReg.waiting_org)
async def reg_event_part8(message: Message, state: FSMContext):
    """
    Store user organization and finish registration.

    Args:
        message (Message): Incoming user message.
        state (FSMContext): FSM context for user.

    Returns:
        None
    """
    await update_reg_event(message.from_user.id, {'org': message.text})
    if await check_completly_reg_event(message.from_user.id):
        data = await state.get_data()
        name = data.get('name')
        await send_event_qr_code(message.from_user.id, name, message, state)
    else:
        await safe_send_message(
            bot, message,
            'Что-то пошло не так, начните регистрацию заново, пожалуйста\n'
            'Для этого повторно перейдите по ссылке'
        )
    await state.clear()
