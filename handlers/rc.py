from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import date

from aiogram.utils.deep_linking import create_start_link
from cryptography.fernet import Fernet

from handlers.error import safe_send_message, make_short_link
from bot_instance import bot
from database.req import (get_user, create_user, add_vacancy, delete_vacancy, get_users_tg_id, get_all_events,
                          get_users_tg_id_in_event, get_random_user_from_event, update_event,
                          get_random_user_from_event_wth_bad, get_all_vacancy_names, get_event, get_all_events_in_p,
                          create_event, get_users_tg_id_in_event_bad, update_user_x_event_row_status, get_add_winner,
                          get_users_unreg_tg_id, get_host, get_all_hosts_in_event_orgs, create_host,
                          get_host_by_org_name, update_strick, get_userrc, create_userrc, update_userrc,
                          get_all_userrcs_wth_coffee)
from keyboards.keyboards import post_target, post_ev_tagret, stat_target, apply_winner, vacancy_selection_keyboard, \
    single_command_button_keyboard, link_ikb, yes_no_link_ikb, unreg_yes_no_link_ikb, get_ref_ikb, yes_no_kb, \
    expections_kb, yes_no_rc_ikb, about_coffee_ikb, coffee_moves, yes_no_change_format_rc_ikb, format_choice_kb
from statistics.stat import get_stat_all, get_stat_all_in_ev, get_stat_quest, get_stat_ad_give_away, get_stat_reg_out, \
    get_stat_reg

router = Router()


# TODO: each saturday
async def may_be_coffee():
    users = await get_all_userrcs_wth_coffee()
    if not users or len(users) == 1:
        await safe_send_message(bot, 483458201, 'У вас нет пользователей для рандом кофе на этой неделе((')
        return
    for user in users:
        if user.dndist > 0:
            await decrease_dndist(user.id)
        if user.dndist <= 1:
            await safe_send_message(bot, user.id, 'Привет!\nВстречи Random Coffee продолжаются.\nУчаствуешь на следующей неделе?\n', reply_markup=about_coffee_ikb())


@router.callback_query(F.data == 'rc_week_yes')
async def cbq_rc_week_yes(callback: CallbackQuery):
    await update_userrc(callback.from_user.id, {'dndist': 0})
    await safe_send_message(bot, callback, 'Все круто, скоро пришлем тебе информацию о твоей паре)')


@router.callback_query(F.data == 'rc_week_no')
async def cbq_rc_week_no(callback: CallbackQuery):
    await update_userrc(callback.from_user.id, {'dndist': 1})
    await safe_send_message(bot, callback, 'Очень ждем тебя через неделю!')


@router.callback_query(F.data == 'rc_mounth_no')
async def cbq_rc_mounth_no(callback: CallbackQuery):
    await update_userrc(callback.from_user.id, {'dndist': 4})
    await safe_send_message(bot, callback, 'Грусна(((')


# TODO: each wednesday (send pairs)
async def your_coffee():
    users = await get_all_userrcs_wth_coffee()
    if not users:
        await safe_send_message(bot, 483458201, 'У вас нет пользователей для рандом кофе на этой неделе((')
        return
    # TODO: maik pairs, choose first from pair and add link lo second person
    for user in users:
        if user.dndist == 0:
            await safe_send_message(bot, user.id, '')  # TODO: write message


# TODO: each friday(sand fb question)
async def how_y_coffee():
    users = await get_all_userrcs_wth_coffee()
    if not users:
        await safe_send_message(bot, 483458201, 'У вас нет пользователей для рандом кофе на этой неделе((')
        return
    for user in users:
        if user.dndist == 0:
            await safe_send_message(bot, user.id, '', reply_markup=)  # TODO: write message


@router.message(Command('random_coffee'))
async def cmd_random_coffee(message: Message, state: FSMContext):
    userrc = await get_userrc(message.from_user.id)
    if not userrc:
        await create_userrc(message.from_user.id)
        await safe_send_message(bot, message, 'Для начала надо зарегистрироваться')
        await start_survey(message, state)
    else:
        if userrc.is_active:
            await safe_send_message(bot, message, 'Это раздел Рандом Кофе в боте Бизнес Клуба Питерской вышки\n\nНовые пары скоро появятся, а пока ты можешь:', reply_markup=coffee_moves())
        else:
            await safe_send_message(bot, message, 'Хотите принять участие в рандом кофе со след раунда?', reply_markup=yes_no_rc_ikb())


@router.callback_query(F.data == 'stop_rc')
async def cbq_stop_rc(callback: CallbackQuery):
    await update_userrc(callback.from_user.id, {'is_active': False})
    await safe_send_message(bot, callback, 'Очень жаль, но мы верим что ты передумаешь')


@router.callback_query(F.data == 'change_format_rc')
async def cbq_change_format_rc(callback: CallbackQuery):
    userrc = await get_userrc(callback.from_user.id)
    await safe_send_message(bot, callback, f'Твой текуший формат встреч - {userrc.format}, хочешь изменить его?', reply_markup=yes_no_change_format_rc_ikb())


@router.callback_query(F.data == 'change_format_rc_no')
async def cbq_change_format_rc_no(callback: CallbackQuery):
    await safe_send_message(bot, callback, "Хорошо, ничего не меняю")


@router.callback_query(F.data == 'change_format_rc_yes')
async def cbq_change_format_rc_yes(callback: CallbackQuery):
    userrc = await get_userrc(callback.from_user.id)
    if userrc.format == 'Онлайн':
        await update_userrc(callback.from_user.id, {'format': 'Офлайн'})
    else:
        await update_userrc(callback.from_user.id, {'format': 'Онлайн'})
    userrc = await get_userrc(callback.from_user.id)
    await safe_send_message(bot, callback, f'Готово, поменяли твой формат встреч на {userrc.format}')


@router.callback_query(F.data == 'rc_no')
async def cbq_rc_no(callback: CallbackQuery):
    await safe_send_message(bot, callback, 'Очень жаль, но мы верим что ты передумаешь')


@router.callback_query(F.data == 'rc_yes')
async def cbq_rc_yes(callback: CallbackQuery):
    await update_userrc(callback.from_user.id, {'is_active': True, 'dndist': 0})
    await safe_send_message(bot, callback, 'Отлично, мы напишем тебе в ХХдень неделиХХ, когда будут готовы пары')


class SurveyState(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_city = State()
    waiting_for_organization = State()
    waiting_for_business = State()
    waiting_for_business_details = State()
    waiting_for_business_interest = State()
    waiting_for_hobby = State()
    waiting_for_specialty = State()
    waiting_for_expectations = State()
    waiting_for_format = State()


async def start_survey(message: Message, state: FSMContext):
    await safe_send_message(bot, message, "Введите ваше ФИО:")
    await state.set_state(SurveyState.waiting_for_full_name)


@router.message(SurveyState.waiting_for_full_name)
async def get_full_name(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'fio': message.text})
    await safe_send_message(bot, message, 'Введите ваш город:')
    await state.set_state(SurveyState.waiting_for_city)


@router.message(SurveyState.waiting_for_city)
async def get_city(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'city': message.text})
    await safe_send_message(bot, message, 'Введите ваш вуз/организацию:')
    await state.set_state(SurveyState.waiting_for_organization)


@router.message(SurveyState.waiting_for_organization)
async def get_organization(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'organization': message.text})
    await safe_send_message(bot, message, "Вы ведете бизнес?", reply_markup=yes_no_kb())
    await state.set_state(SurveyState.waiting_for_business)


@router.message(SurveyState.waiting_for_business)
async def get_business(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'business': message.text})
    if message.text.lower() == "да":
        await message.answer("Чем вы занимаетесь?")
        await state.set_state(SurveyState.waiting_for_business_details)
    else:
        await safe_send_message(bot, message, "Хотели бы начать бизнес?", reply_markup=yes_no_kb())
        await state.set_state(SurveyState.waiting_for_business_interest)


@router.message(SurveyState.waiting_for_business_details)
async def get_business_details(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'business_details': message.text})
    await safe_send_message(bot, message, "Ваши хобби:")
    await state.set_state(SurveyState.waiting_for_hobby)


@router.message(SurveyState.waiting_for_business_interest)
async def get_business_interest(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'business_interest': message.text})
    await safe_send_message(bot, message, "Ваши хобби:")
    await state.set_state(SurveyState.waiting_for_hobby)


@router.message(SurveyState.waiting_for_hobby)
async def get_hobby(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'hobby': message.text})
    await safe_send_message(bot, message, "Область образования/специальность:")
    await state.set_state(SurveyState.waiting_for_specialty)


@router.message(SurveyState.waiting_for_specialty)
async def get_specialty(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'specialty': message.text})
    await safe_send_message(bot, message, "Ожидания от встречи:", reply_markup=expections_kb())
    await state.set_state(SurveyState.waiting_for_expectations)


@router.message(SurveyState.waiting_for_expectations)
async def get_expectations(message: Message, state: FSMContext):
    await update_userrc(message.from_user.id, {'expectations': message.text})
    await safe_send_message(bot, message, "Укажите предпочитаемый формат встреч, пожалуйста", reply_markup=format_choice_kb())
    await state.set_state(SurveyState.waiting_for_format)


@router.message(SurveyState.waiting_for_format)
async def get_expectations(message: Message, state: FSMContext):
    if message.text.lower() not in ['офлайн', 'онлайн']:
        await safe_send_message(bot, message, 'Выберете что то с клавиатуры, пожалуйста', reply_markup=format_choice_kb())
        return
    await update_userrc(message.from_user.id, {'format': message.text, 'is_quest': True})
    await safe_send_message(bot, message, "Спасибо за регистрацию!")
    await state.clear()
    await cmd_random_coffee(message, state)
