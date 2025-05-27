"""
Face control-related keyboard layouts.
"""
# --------------------------------------------------------------------------------

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# --------------------------------------------------------------------------------

def face_checkout_kb(user_id: int, event_name: str) -> InlineKeyboardMarkup:
    """
    Create keyboard for face control checkout.

    Args:
        user_id (int): User ID to verify.
        event_name (str): Event name.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Пропустить",
                callback_data=f"verify_{user_id}_{event_name}_allow"
            ),
            InlineKeyboardButton(
                text="❌ Не пропускать",
                callback_data=f"verify_{user_id}_{event_name}_deny"
            )
        ]
    ])
    return keyboard


def back_to_face_control() -> InlineKeyboardMarkup:
    """
    Create back button keyboard for face control.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="face_control")]
    ])
    return keyboard


def face_control_menu_kb() -> InlineKeyboardMarkup:
    """
    Create main menu keyboard for face control.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить фейс-контроль", callback_data="face_control_add"),
            InlineKeyboardButton(text="➖ Удалить фейс-контроль", callback_data="face_control_remove")
        ],
        [InlineKeyboardButton(text="📋 Список фейс-контроль", callback_data="face_control_list")]
    ])
    return keyboard


def face_controls_list(face_controls) -> InlineKeyboardMarkup:
    """
    Create keyboard with list of face control users.

    Args:
        face_controls: List of face control objects.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"@{fc.username or 'No username'} ({fc.user_id})",
            callback_data=f"face_control_remove_{fc.user_id}"
        )]
        for fc in face_controls
    ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="face_control")])
    return keyboard


def yes_no_face(user_id: int) -> InlineKeyboardMarkup:
    """
    Create confirmation keyboard for face control actions.

    Args:
        user_id (int): User ID to confirm action for.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"face_control_confirm_remove_{user_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="face_control_cancel_remove")
        ]
    ])
    return keyboard
