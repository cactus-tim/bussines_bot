"""
Event Keyboards
Inline and reply keyboards related to event interactions.
"""

# --------------------------------------------------------------------------------

from aiogram.types import (
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from keyboards.club_events.common.utils import make_k_from_list

# --------------------------------------------------------------------------------

def vacancy_selection_keyboard(vacancies: list[str]) -> ReplyKeyboardMarkup:
    """
    Create reply keyboard for selecting vacancies.

    Args:
        vacancies (list[str]): Available vacancy names.

    Returns:
        ReplyKeyboardMarkup: Reply keyboard markup.
    """
    keyboard = make_k_from_list(vacancies)
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )

# --------------------------------------------------------------------------------

def another_vacancy_keyboard() -> InlineKeyboardMarkup:
    """
    Create inline keyboard to ask another vacancy selection.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [InlineKeyboardButton(text="Нет", callback_data="another_no")],
        [InlineKeyboardButton(
            text="Да, хочу подать заявление на еще одну вакансию",
            callback_data="another_yes",
        )],
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def events_ikb(events: list) -> InlineKeyboardMarkup:
    """
    Create inline keyboard from event objects.

    Args:
        events (list): List of event objects with desc and name.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [
        [InlineKeyboardButton(text=ev.desc, callback_data=ev.name)]
        for ev in events
    ]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def get_ref_ikb(event_name: str) -> InlineKeyboardMarkup:
    """
    Create inline keyboard to get referral link.

    Args:
        event_name (str): Event identifier.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(
        text="Получить реферальную ссылку на это мероприятие",
        callback_data=event_name
    )]]
    return InlineKeyboardMarkup(inline_keyboard=ikb)

# --------------------------------------------------------------------------------

def choose_event_for_qr(events: list) -> InlineKeyboardMarkup:
    """
    Create keyboard for choosing event to get QR code.

    Args:
        events (list): List of event objects.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ev.desc, callback_data=f"qr_{ev.name}")]
        for ev in events
    ])
    return keyboard
