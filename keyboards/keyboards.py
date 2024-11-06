from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from math import ceil

from database.req import get_all_vacancy_names


def make_k_from_list(a: list) -> list:
    rows_cnt = ceil(len(a) / 3)
    keyboard = []
    for i in range(0, rows_cnt - 1):
        keyboard.append([KeyboardButton(text=a[0 + (i * 3)]), KeyboardButton(text=a[1 + (i * 3)]),
                         KeyboardButton(text=a[2 + (i * 3)])])
    keyboard.append([KeyboardButton(text=a[i + ((rows_cnt - 1) * 3)]) for i in range(0, len(a) % 3)])
    return keyboard


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
        [InlineKeyboardButton(text="Всем участникам ивента", callback_data="post_to_ev")],
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


def stat_target():
    ikb = [
        [InlineKeyboardButton(text="Всех пользователей", callback_data="stat_all")],
        [InlineKeyboardButton(text="Всех участников ивента", callback_data="stat_ev")],
        # [InlineKeyboardButton(text="Всех из опроса", callback_data="stat_quest")],
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
        keyboard=[[KeyboardButton(text="Анкета для отбора в команду")]],
        resize_keyboard=True
    )
    return keyboard


def quest_keyboard():
    ikb = [
        [InlineKeyboardButton(text='Стать частью команды HSE SPB Business Club', url='https://forms.gle/SHYAncupSwvmSEZp7')]
    ]
    ikeyboard = InlineKeyboardMarkup(inline_keyboard=ikb)
    return ikeyboard
