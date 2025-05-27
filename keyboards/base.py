"""
Common Keyboards
Reusable inline and reply keyboard layouts for user interaction.
"""

# --------------------------------------------------------------------------------

from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

# --------------------------------------------------------------------------------

def main_reply_keyboard() -> ReplyKeyboardMarkup:
    """
    Create single-button reply keyboard.

    Returns:
        ReplyKeyboardMarkup: Reply keyboard markup.
    """
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Получить QR-код")]],
        resize_keyboard=True,
    )

# --------------------------------------------------------------------------------

def link_ikb(text: str, url: str) -> InlineKeyboardMarkup:
    """
    Create inline keyboard with a URL button.

    Args:
        text (str): Button text.
        url (str): Link URL.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(text=text, url=url)]]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def yes_no_ikb() -> InlineKeyboardMarkup:
    """
    Create inline yes/no keyboard.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='event_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='event_no'),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def yes_no_hse_ikb() -> InlineKeyboardMarkup:
    """
    Create HSE-specific yes/no keyboard.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='hse_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='hse_no'),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def yes_no_link_ikb() -> InlineKeyboardMarkup:
    """
    Create yes/no/cancel keyboard with link prompt.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='link_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='link_no'),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def unreg_yes_no_link_ikb() -> InlineKeyboardMarkup:
    """
    Create unregistered yes/no/cancel keyboard.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='unreg_link_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='unreg_link_no'),
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)
