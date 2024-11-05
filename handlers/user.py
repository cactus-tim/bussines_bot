from aiogram.filters import Command, CommandStart
from aiogram import Router, F
from aiogram.filters.command import CommandObject
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from error import safe_send_message
from bot_instance import bot
from database.req import get_user, create_user, create_user_x_event_row
from keyboards.keyboards import confirm_qr


router = Router()


class QRActivationState(StatesGroup):
    awaiting_confirmation = State()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    hash_value = command.args
    if hash_value:
        user = await get_user(message.from_user.id)
        if not user:
            await create_user(message.from_user.id, {'handler': message.from_user.username})
        await state.update_data(hash_value=hash_value)

        await safe_send_message(bot, message, text="Вы хотите активировать этот QR-код?", reply_markup=confirm_qr())
        await state.set_state(QRActivationState.awaiting_confirmation)
    else:
        await create_user(message.from_user.id, {'handler': message.from_user.username})
        await safe_send_message(bot, message, text="Какое-то приветственное сообщение")


@router.callback_query(F.data == "confirm_qr")
async def cmd_confirm_qr(callback: F.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    event_name = data.get('hash_value')
    await create_user_x_event_row(callback.message.from_user.id, event_name)
    await safe_send_message(bot, callback, text="QR-код удачно использован")
    await state.clear()


@router.callback_query(F.data == "cancel_qr")
async def cmd_cancel_qr(callback: F.CallbackQuery, state: FSMContext):
    await safe_send_message(bot, callback, text="Использование QR-кода отменено")
    await state.clear()


@router.message(Command("info"))
async def cmd_info(message: Message):
    user = await get_user(message.from_user.id)
    if user.is_superuser:
        await safe_send_message(bot, message, text="Список доступных команд:"
                                                   "\\start - перезапуск бота"
                                                   "\\info - информация о доступных комнадах"
                                                   "\\quest - пройти анкетирование для отбора в команду"
                                                   "\\send_stat"
                                                   "\\send_post"
                                                   "\\add_vacancy"
                                                   "\\dell_vacancy"
                                                   "\\add_event"
                                                   "\\end_event"
                                                   "\\all_vacancies")
    else:
        await safe_send_message(bot, message, text="Список доступных команд:"
                                                   "\\start - перезапуск бота"
                                                   "\\info - информация о доступных комнадах"
                                                   "\\quest - пройти анкетирование для отбора в команду")
