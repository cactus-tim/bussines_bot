"""
Face Control Management
Bot handlers for assigning, removing, and listing face control users.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from database.req import get_user
from database.req.face_control import (
    add_face_control, get_face_control, list_face_control, remove_face_control
)
from handlers.error import safe_send_message
from handlers.states import FaceControlState
from keyboards.keyboards import (
    face_control_menu_kb, back_to_face_control,
    face_controls_list, yes_no_face
)

# --------------------------------------------------------------------------------

router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


# --------------------------------------------------------------------------------

@router.message(Command("face_control"))
async def cmd_face_control(message: Message):
    """
    Show face control management menu.

    Args:
        message (Message): The incoming command message.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return

    await safe_send_message(
        bot, message,
        "Управление фейс-контроль:\n"
        "• Добавить - назначить нового фейс-контроль\n"
        "• Удалить - снять права фейс-контроль\n"
        "• Список - просмотреть всех фейс-контроль",
        reply_markup=face_control_menu_kb()
    )


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "face_control")
async def face_control_menu(callback: CallbackQuery):
    """
    Show face control management menu via callback.

    Args:
        callback (CallbackQuery): The callback query.

    Returns:
        None
    """
    user = await get_user(callback.from_user.id)
    if not user.is_superuser:
        return

    await callback.message.edit_text(
        "Управление фейс-контроль:\n"
        "• Добавить - назначить нового фейс-контроль\n"
        "• Удалить - снять права фейс-контроль\n"
        "• Список - просмотреть всех фейс-контроль",
        reply_markup=face_control_menu_kb()
    )


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "face_control_add")
async def face_control_add(callback: CallbackQuery, state: FSMContext):
    """
    Start process of adding a face control user.

    Args:
        callback (CallbackQuery): The callback query.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    user = await get_user(callback.from_user.id)
    if not user.is_superuser:
        return

    await callback.message.edit_text(
        "Введите Telegram ID пользователя, которого хотите назначить фейс-контроль.\n"
        "ID можно получить, если пользователь перешлет сообщение от @getmyid_bot",
        reply_markup=back_to_face_control()
    )
    await state.set_state(FaceControlState.waiting_user_id)


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "face_control_remove")
async def face_control_remove(callback: CallbackQuery):
    """
    Show list of face control users to remove.

    Args:
        callback (CallbackQuery): The callback query.

    Returns:
        None
    """
    user = await get_user(callback.from_user.id)
    if not user.is_superuser:
        return

    face_controls = await list_face_control()
    if not face_controls:
        await callback.message.edit_text(
            "Нет назначенных фейс-контроль",
            reply_markup=back_to_face_control()
        )
        return

    await callback.message.edit_text(
        "Выберите пользователя, которого хотите снять с фейс-контроль:",
        reply_markup=face_controls_list(face_controls)
    )


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "face_control_list")
async def face_control_list(callback: CallbackQuery):
    """
    List all face control users.

    Args:
        callback (CallbackQuery): The callback query.

    Returns:
        None
    """
    try:
        face_control_users = await list_face_control()
        if not face_control_users:
            await callback.message.edit_text(
                "Нет назначенных фейс-контроль",
                reply_markup=back_to_face_control()
            )
            return

        msg = "Список фейс-контроль:\n\n"
        for fc in face_control_users:
            msg += f"- {fc.user_id} @{fc.username or 'не указан'}\n"

        await callback.message.edit_text(msg, reply_markup=back_to_face_control())

    except Exception as e:
        print(f"Error listing face control users: {e}")
        await callback.answer("Произошла ошибка при получении списка фейс-контроль")


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("face_control_remove_"))
async def face_control_remove_confirm(callback: CallbackQuery, state: FSMContext):
    """
    Confirm removal of face control user.

    Args:
        callback (CallbackQuery): The callback query.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    user = await get_user(callback.from_user.id)
    if not user.is_superuser:
        return

    user_id = int(callback.data.split("_")[-1])
    face_control = await get_face_control(user_id)
    if face_control == "not found":
        await callback.answer("Пользователь не найден")
        return

    await callback.message.edit_text(
        f"Вы уверены, что хотите снять права фейс-контроль у пользователя @{face_control.username or 'No username'}?",
        reply_markup=yes_no_face(user_id)
    )


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("face_control_confirm_remove_"))
async def face_control_remove_execute(callback: CallbackQuery):
    """
    Execute removal of face control user.

    Args:
        callback (CallbackQuery): The callback query.

    Returns:
        None
    """
    user = await get_user(callback.from_user.id)
    if not user.is_superuser:
        return

    user_id = int(callback.data.split("_")[-1])
    success = await remove_face_control(user_id)
    keyboard = back_to_face_control()

    if success:
        await callback.message.edit_text("✅ Пользователь снят с фейс-контроль", reply_markup=keyboard)
    else:
        await callback.message.edit_text("❌ Не удалось снять пользователя с фейс-контроль", reply_markup=keyboard)


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "face_control_cancel_remove")
async def face_control_cancel_remove(callback: CallbackQuery):
    """
    Cancel removal of face control user.

    Args:
        callback (CallbackQuery): The callback query.

    Returns:
        None
    """
    await callback.message.edit_text("❌ Операция отменена")


# --------------------------------------------------------------------------------

@router.message(FaceControlState.waiting_user_id)
async def face_control_add_process(message: Message, state: FSMContext):
    """
    Process adding a new face control user.

    Args:
        message (Message): The user message with ID.
        state (FSMContext): The FSM context.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return

    try:
        user_id = int(message.text)
        target_user = await get_user(user_id)
        if target_user == "not created":
            await safe_send_message(bot, message, "❌ Пользователь не найден в базе бота")
            await state.clear()
            return

        existing = await get_face_control(user_id)
        if existing != "not found":
            await safe_send_message(bot, message, "❌ Пользователь уже является фейс-контроль")
            await state.clear()
            return

        await add_face_control(
            user_id=user_id,
            admin_id=message.from_user.id,
            username=target_user.handler,
            full_name=""
        )

        await safe_send_message(
            bot, message,
            f"✅ Пользователь @{target_user.handler} назначен фейс-контроль",
            reply_markup=back_to_face_control()
        )

    except ValueError:
        await safe_send_message(bot, message, "❌ Неверный формат ID. Введите числовой ID пользователя")

    except Exception as e:
        print(f"Error adding face control: {e}")
        await safe_send_message(bot, message, "❌ Произошла ошибка при назначении фейс-контроль")

    await state.clear()
