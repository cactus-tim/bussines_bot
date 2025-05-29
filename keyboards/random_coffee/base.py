"""
Random Coffee Keyboards

Inline keyboards for city, goal, format, profile editing and feedback.
"""

# --------------------------------------------------------------------------------

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --------------------------------------------------------------------------------

def get_city_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for city selection.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with city options.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Москва", callback_data="city_moscow")],
            [InlineKeyboardButton(text="Санкт-Петербург", callback_data="city_spb")],
            [InlineKeyboardButton(text="Другой город", callback_data="city_other")],
        ]
    )

# --------------------------------------------------------------------------------

def get_meeting_goal_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for meeting goal selection.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with meeting goal options.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="10% фан / 90% польза", callback_data="goal_10-90")],
            [InlineKeyboardButton(text="30% фан / 70% польза", callback_data="goal_30-70")],
            [InlineKeyboardButton(text="50% фан / 50% польза", callback_data="goal_50-50")],
            [InlineKeyboardButton(text="70% фан / 30% польза", callback_data="goal_70-30")],
            [InlineKeyboardButton(text="90% фан / 10% польза", callback_data="goal_90-10")]
        ]
    )

# --------------------------------------------------------------------------------

def get_meeting_format_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for meeting format selection.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with format options.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Онлайн", callback_data="format_online")],
            [InlineKeyboardButton(text="Вживую", callback_data="format_offline")]
        ]
    )

# --------------------------------------------------------------------------------

def get_weekly_participation_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard for weekly participation confirmation.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with participation options.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да, участвовать", callback_data="participate_yes")],
            [InlineKeyboardButton(text="Нет, пропустить", callback_data="participate_no")],
            [InlineKeyboardButton(text="Посмотреть и изменить анкету", callback_data="view_profile")]
        ]
    )

# --------------------------------------------------------------------------------

def cancel_weekly_participation_keyboard() -> InlineKeyboardMarkup:
    """
    Get keyboard to cancel weekly participation.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with cancel button.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Отменить участие на этой неделе", callback_data="participate_no")]
        ]
    )

# --------------------------------------------------------------------------------

def get_profile_edit_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for profile editing.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with profile fields to edit.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="ФИО", callback_data="edit_fullname"),
                InlineKeyboardButton(text="Город", callback_data="edit_city")
            ],
            [
                InlineKeyboardButton(text="Соц. сети", callback_data="edit_social"),
                InlineKeyboardButton(text="Род деятельности", callback_data="edit_occupation")
            ],
            [
                InlineKeyboardButton(text="Хобби", callback_data="edit_hobbies"),
                InlineKeyboardButton(text="Дата рождения", callback_data="edit_birth_date")
            ],
            [
                InlineKeyboardButton(text="Цель знакомства", callback_data="edit_goal"),
                InlineKeyboardButton(text="Формат встреч", callback_data="edit_format")
            ]
        ]
    )

# --------------------------------------------------------------------------------

def get_feedback_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard for meeting feedback.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with rating options 1–5.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⭐️", callback_data="rate_1")],
            [InlineKeyboardButton(text="⭐️⭐️", callback_data="rate_2")],
            [InlineKeyboardButton(text="⭐️⭐️⭐️", callback_data="rate_3")],
            [InlineKeyboardButton(text="⭐️⭐️⭐️⭐️", callback_data="rate_4")],
            [InlineKeyboardButton(text="⭐️⭐️⭐️⭐️⭐️", callback_data="rate_5")]
        ]
    )

# --------------------------------------------------------------------------------

def user_send_message_kb(user_id: int) -> InlineKeyboardMarkup:
    """
    Get inline keyboard with a direct link to message a user.

    Args:
        user_id (int): Telegram user ID.

    Returns:
        InlineKeyboardMarkup: Inline keyboard with a link button.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Написать собеседнику",
                    url=f"tg://user?id={user_id}"
                )
            ]
        ]
    )
