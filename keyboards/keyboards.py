from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from math import ceil, floor

from database.req import get_all_vacancy_names


def make_k_from_list(a: list[str]) -> list[list[KeyboardButton]]:
    keyboard: list[KeyboardButton] = [KeyboardButton(text=el) for el in a]
    result: list[list[KeyboardButton]] = [[]]
    row = 0
    for button in keyboard:
        if len(result[row]) == 3:
            result.append([])
            row += 1
        result[row].append(button)
    return result


def vacancy_selection_keyboard(vacancies: list):
    keyboard = make_k_from_list(vacancies)
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
    return keyboard


def another_vacancy_keyboard():
    ikb = [
        [InlineKeyboardButton(text="Нет", callback_data="another_no")],
        [InlineKeyboardButton(text="Да, хочу подать заявление на еще одну вакансию", callback_data="another_yes")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def post_target():
    ikb = [
        [InlineKeyboardButton(text="Всем пользователям", callback_data="post_to_all")],
        [InlineKeyboardButton(text="Всем пользователям, незареганным на ивент", callback_data="post_to_unreg")],
        [InlineKeyboardButton(text="Всем участникам ивента", callback_data="post_to_ev")],
        [InlineKeyboardButton(text="Обратная связь от всех участников ивента", callback_data="post_wth_op_to_ev")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def post_ev_tagret(events: list):
    keyboard = make_k_from_list(events)
    keyboard = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )
    return keyboard


def events_ikb(events: list):
    ikb = [[InlineKeyboardButton(text=ev.desc, callback_data=ev.name)] for ev in events]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def stat_target():
    ikb = [
        [InlineKeyboardButton(text="Всех пользователей", callback_data="stat_all")],
        [InlineKeyboardButton(text="Всех участников ивента", callback_data="stat_ev")],
        # [InlineKeyboardButton(text="Всех из опроса", callback_data="stat_quest")],
        [InlineKeyboardButton(text="Всех участников дополнительного розыгрыша", callback_data="stat_give_away")],
        [InlineKeyboardButton(text="Всех зареганых на ивент, не из ВШЭ", callback_data="stat_reg_out")],
        [InlineKeyboardButton(text="Всех зареганых на ивент + статистика", callback_data="stat_reg")],
        [InlineKeyboardButton(text="Отмена", callback_data="cancel")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def apply_winner():
    ikb = [
        [InlineKeyboardButton(text="Он здесь, все хорошо", callback_data="confirm")],
        [InlineKeyboardButton(text="Его нет, нужен реролл", callback_data="reroll")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def single_command_button_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Стать частью команды HSE SPB Business Club")]],
        resize_keyboard=True
    )
    return keyboard


def quest_keyboard_1():
    ikb = [
        [InlineKeyboardButton(text='Приступить к первому этапу', callback_data="next")]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def quest_keyboard_2():
    ikb = [
        [InlineKeyboardButton(text='Анкета для отбора в команду', url='https://forms.gle/SHYAncupSwvmSEZp7')]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def link_ikb(text, url):
    ikb = [
        [InlineKeyboardButton(text=text, url=url)]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def yes_no_ikb():
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='event_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='event_no')
         ]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def yes_no_hse_ikb():
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='hse_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='hse_no')
         ]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def yes_no_link_ikb():
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='link_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='link_no'),
            InlineKeyboardButton(text="Отмена", callback_data="cancel")
         ]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def unreg_yes_no_link_ikb():
    ikb = [
        [
            InlineKeyboardButton(text='ДА', callback_data='unreg_link_yes'),
            InlineKeyboardButton(text='НЕТ', callback_data='unreg_link_no'),
            InlineKeyboardButton(text="Отмена", callback_data="cancel")
         ]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def get_ref_ikb(event_name: str):
    ikb = [
        [InlineKeyboardButton(text="Получить реферальную ссылку на это мероприятие", callback_data=event_name)]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard


def top_ikb():
    ikb = [
        [InlineKeyboardButton(text="Топ пользователей", callback_data='top')]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard
