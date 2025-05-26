"""
Keyboards
Keyboard markup builders for bot commands.
"""

# --------------------------------------------------------------------------------
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)


# --------------------------------------------------------------------------------
def make_k_from_list(items: list[str]) -> list[list[KeyboardButton]]:
    """
    Build keyboard layout from list of strings.

    Args:
        items (list[str]): List of button labels.

    Returns:
        list[list[KeyboardButton]]: 2D list of KeyboardButton rows.
    """
    buttons = [KeyboardButton(text=el) for el in items]
    result: list[list[KeyboardButton]] = [[]]
    row = 0
    for btn in buttons:
        if len(result[row]) == 3:
            result.append([])
            row += 1
        result[row].append(btn)
    return result


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
def single_command_button_keyboard() -> ReplyKeyboardMarkup:
    """
    Create single-button reply keyboard.

    Returns:
        ReplyKeyboardMarkup: Reply keyboard markup.
    """
    return ReplyKeyboardMarkup(
        # keyboard=[[KeyboardButton(text="Стать частью команды HSE SPB Business Club")]],
        keyboard=[[KeyboardButton(text="Получить QR-код")]],
        resize_keyboard=True,
    )


# --------------------------------------------------------------------------------
def quest_keyboard_1() -> InlineKeyboardMarkup:
    """
    Create inline keyboard for first quest step.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(text='Приступить к первому этапу', callback_data="next")]]
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


# --------------------------------------------------------------------------------
def get_ref_ikb(event_name: str) -> InlineKeyboardMarkup:
    """
    Create inline keyboard to get referral link.

    Args:
        event_name (str): Event identifier.

    Returns:
        InlineKeyboardMarkup: Inline keyboard markup.
    """
    ikb = [[InlineKeyboardButton(text="Получить реферальную ссылку на это мероприятие", callback_data=event_name)]]
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

def face_checkout_kb(user_id: int, event_name:str) -> InlineKeyboardMarkup:
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

def choose_event_for_qr(events:list) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=ev.desc, callback_data=f"qr_{ev.name}")]
        for ev in events
    ])
    return keyboard

def back_to_face_control():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="◀️ Назад", callback_data="face_control")]
    ])
    return keyboard

def face_control_menu_kb():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="➕ Добавить фейс-контроль", callback_data="face_control_add"),
            InlineKeyboardButton(text="➖ Удалить фейс-контроль", callback_data="face_control_remove")
        ],
        [InlineKeyboardButton(text="📋 Список фейс-контроль", callback_data="face_control_list")]
    ])
    return keyboard

def face_controls_list(face_controls):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"@{fc.username or 'No username'} ({fc.user_id})",
            callback_data=f"face_control_remove_{fc.user_id}"
        )]
        for fc in face_controls
    ])
    keyboard.inline_keyboard.append([InlineKeyboardButton(text="◀️ Назад", callback_data="face_control")])
    return keyboard

def yes_no_face(user_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"face_control_confirm_remove_{user_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data="face_control_cancel_remove")
        ]
    ])

    return keyboard