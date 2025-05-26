from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
import logging

from config.settings import TOKEN
from config.texts.commands import WELCOME_MESSAGE
from database.req import get_user, create_user, create_user_x_event_row, get_event, \
    update_user_x_event_row_status, update_reg_event, check_completly_reg_event, create_reg_event, get_reg_event, \
    get_user_x_event_row, get_ref_give_away, create_ref_give_away, delete_user_x_event_row, delete_ref_give_away_row, \
    get_all_hosts_in_event_ids, get_host, add_money, one_more_event, add_referal_cnt, update_strick, \
    add_user_to_networking
from handlers.error import safe_send_message
from handlers.public.quest import start
from handlers.public.qr import cmd_check_qr, send_event_qr_code
from handlers.states import EventReg
from keyboards.keyboards import single_command_button_keyboard, yes_no_ikb, yes_no_hse_ikb, get_ref_ikb

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)


async def create_user_if_not_exists(user_id: int, username: str, first_contact: str = None) -> str:
    """Create user if not exists and return user status."""
    user = await get_user(user_id)
    if user == "not created":
        user_data = {'handler': username}
        if first_contact:
            user_data['first_contact'] = first_contact
        await create_user(user_id, user_data)
    return user


async def send_welcome_message(user_id: int, username: str, message: Message):
    """Send welcome message to user."""
    name = message.from_user.first_name if message.from_user.first_name else username
    await safe_send_message(bot, message, text=WELCOME_MESSAGE.format(name=name),
                            reply_markup=single_command_button_keyboard())


async def handle_networking_hash(user_id: int, username: str, message: Message):
    """Handle networking hash value."""
    await create_user_if_not_exists(user_id, username, 'networking')
    flag = await add_user_to_networking(user_id)
    if not flag:
        await safe_send_message(bot, user_id, 'Вы уже участвуете в нетворкинге')
    else:
        await safe_send_message(bot, user_id, 'Поздравляем! Вы участвуете в нетворкинге')
    await bot.delete_message(user_id, message.message_id - 1)


async def handle_reg_hash(user_id: int, username: str, hash_value: str, message: Message, state: FSMContext):
    """Handle registration hash value."""
    await create_user_if_not_exists(user_id, username, hash_value[4:])

    event_name = hash_value.split('_')[1] + '_' + hash_value.split('_')[2] + '_' + hash_value.split('_')[3]
    user_x_event = await get_user_x_event_row(user_id, event_name)
    if user_x_event == 'not created':
        await create_user_x_event_row(user_id, event_name, hash_value.split('_')[-1])
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


async def handle_ref_hash(user_id: int, username: str, hash_value: str, message: Message, state: FSMContext):
    """Handle referral hash value."""
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
        await safe_send_message(bot, message, f'Хотите зарегистрироваться на мероприятие "{event.desc}",'
                                              f'которое пройдет {event.date} в {event.time}',
                                reply_markup=yes_no_ikb())
        hosts_ids = await get_all_hosts_in_event_ids(event_name)
        if hosts_ids and ref_user_id in hosts_ids:
            ref_give_away = await get_ref_give_away(user_id, event_name)
            if not ref_give_away:
                await create_ref_give_away(user_id, event_name, ref_user_id)
                host = await get_host(ref_user_id, event_name)
                await safe_send_message(bot, message,
                                        f'Поздравляю, вы участвуете в розыгрыше, предназначенным только для подписчиков @{host.org_name}')
            else:
                await safe_send_message(bot, message, 'Вы уже участвуете в чьем то розыгрыше')
        await safe_send_message(bot, ref_user_id, f"По твоей реферальной ссылке зарегистрировался на событие"
                                                  f" пользователь @{username}!")
    else:
        await safe_send_message(bot, message, 'Вы уже зарегистрировались на это мероприятие',
                                reply_markup=get_ref_ikb(event_name))


async def handle_otbor_hash(user_id: int, username: str, message: Message):
    """Handle otbor hash value."""
    await create_user_if_not_exists(user_id, username, 'otbor')
    name = message.from_user.first_name if message.from_user.first_name else username
    await safe_send_message(bot, message, f'Привет, {name}!', reply_markup=single_command_button_keyboard())
    await start(message)


async def handle_default_hash(user_id: int, username: str, hash_value: str, message: Message):
    """Handle default hash value."""
    user = await create_user_if_not_exists(user_id, username, hash_value)
    if user == "not created":
        await send_welcome_message(user_id, username, message)
    
    row = await update_user_x_event_row_status(user_id, hash_value, 'been')
    if not row:
        await create_user_x_event_row(user_id, hash_value, '0')
        row = await update_user_x_event_row_status(user_id, hash_value, 'been')
    await add_money(user_id, 1)
    await one_more_event(user_id)
    await update_strick(user_id)
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
        await safe_send_message(bot, user_id,
                                f'Вы получили монетку за то что вы зарегистрировались по реферальной ссылке @{ref_giver.handler}!')
        await add_money(user_id, 1)


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext):
    hash_value = command.args
    user_id = message.from_user.id
    username = message.from_user.username

    if hash_value and hash_value.startswith('qr_'):
        # Create a new command object for check_qr
        check_qr_command = CommandObject(command=message.text, args=hash_value)
        await cmd_check_qr(message, check_qr_command)
        return

    if hash_value:
        if hash_value == 'networking':
            await handle_networking_hash(user_id, username, message)
        elif hash_value[:3] == 'reg':
            await handle_reg_hash(user_id, username, hash_value, message, state)
        elif hash_value[:3] == 'ref':
            await handle_ref_hash(user_id, username, hash_value, message, state)
        elif hash_value == 'otbor':
            await handle_otbor_hash(user_id, username, message)
        else:
            await handle_default_hash(user_id, username, hash_value, message)
    else:
        await create_user_if_not_exists(user_id, username)
        await send_welcome_message(user_id, username, message)
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
    await send_event_qr_code(callback.from_user.id, name, callback, state)


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
        await send_event_qr_code(callback.from_user.id, name, callback, state)
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
        await send_event_qr_code(message.from_user.id, name, message, state)
    else:
        await safe_send_message(bot, message, 'Что то пошло не так, начните регистрацию заново, пожалуйста\n'
                                              'Для этого повторно перейдите по ссылке')
    await state.clear()
