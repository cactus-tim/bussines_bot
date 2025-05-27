"""
Admin Keyboards
Inline and reply keyboards for admin-related actions.
"""

# --------------------------------------------------------------------------------

from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from keyboards.club_events.common.utils import make_k_from_list


# --------------------------------------------------------------------------------

def post_target() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for post targeting options.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [InlineKeyboardButton(text="Всем пользователям", callback_data="post_to_all")],
        [InlineKeyboardButton(
            text="Всем пользователям, незареганным на ивент",
            callback_data="post_to_unreg",
        )],
        [InlineKeyboardButton(text="Всем участникам ивента", callback_data="post_to_ev")],
        [InlineKeyboardButton(
            text="Обратная связь от всех участников ивента",
            callback_data="post_wth_op_to_ev",
        )],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)


# --------------------------------------------------------------------------------

def post_ev_target(events: list[str]) -> ReplyKeyboardMarkup:
    """
    Create reply keyboard for selecting event target.

    Args:
        events (list[str]): List of event identifiers.

    Returns:
        ReplyKeyboardMarkup: Reply keyboard markup.
    """
    keyboard = make_k_from_list(events)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


# --------------------------------------------------------------------------------

def stat_target() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for statistics targets.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [InlineKeyboardButton(text="Всех пользователей", callback_data="stat_all")],
        [InlineKeyboardButton(text="Всех участников ивента", callback_data="stat_ev")],
        [InlineKeyboardButton(
            text="Всех участников дополнительного розыгрыша",
            callback_data="stat_give_away",
        )],
        [InlineKeyboardButton(
            text="Всех зареганых на ивент, не из ВШЭ",
            callback_data="stat_reg_out",
        )],
        [InlineKeyboardButton(
            text="Всех зареганых на ивент + статистика",
            callback_data="stat_reg",
        )],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)


# --------------------------------------------------------------------------------

def apply_winner() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for winner confirmation.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [InlineKeyboardButton(text="Он здесь, все хорошо", callback_data="confirm")],
        [InlineKeyboardButton(text="Его нет, нужен реролл", callback_data="reroll")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)


# --------------------------------------------------------------------------------

def top_ikb() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for top users command.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(text="Топ пользователей", callback_data='top')]]
    return InlineKeyboardMarkup(inline_keyboard=ikb)
