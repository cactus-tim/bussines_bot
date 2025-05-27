"""
Quest Keyboards
Inline keyboards for quest interaction steps.
"""

# --------------------------------------------------------------------------------

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

# --------------------------------------------------------------------------------

def quest_keyboard_1() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for first quest step.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(
        text='Приступить к первому этапу',
        callback_data="quest_next"
    )]]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def quest_keyboard_2() -> InlineKeyboardMarkup:
    """
    Create inline keyboard with external quest link.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(
        text='Анкета для отбора в команду',
        url='https://forms.gle/SHYAncupSwvmSEZp7',
    )]]
    return InlineKeyboardMarkup(inline_keyboard=ikb)
