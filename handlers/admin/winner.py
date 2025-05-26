from aiogram import Router, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from config.settings import TOKEN
from database.req import (get_user, get_all_events, get_all_hosts_in_event_orgs, get_host_by_org_name, get_add_winner)
from handlers.error import safe_send_message
from handlers.states import WinnerState
from keyboards.keyboards import post_ev_target, single_command_button_keyboard

router = Router()

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML, ), )


@router.message(Command('get_result'))
async def cmd_get_result(message: Message, state: FSMContext):
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, message, text="У вас нет событий", reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, message, text="Выберете событие:", reply_markup=post_ev_target(events))
    await state.set_state(WinnerState.wait_give_away_event)


@router.message(WinnerState.wait_give_away_event)
async def get_result(message: Message, state: FSMContext):
    await state.update_data({'event_name': message.text})
    hosts_orgs = await get_all_hosts_in_event_orgs(message.text)
    if not hosts_orgs:
        await safe_send_message(bot, message, text="У вас нет организаторов дополнительных розыгрышей",
                                reply_markup=single_command_button_keyboard())
        await state.clear()
        return
    await safe_send_message(bot, message, text="Выберете организатора:\n\nДля отмены введите quit'",
                            reply_markup=post_ev_target(hosts_orgs))
    await state.set_state(WinnerState.wait_give_away_id)


@router.message(WinnerState.wait_give_away_id)
async def get_result2(message: Message, state: FSMContext):
    data = await state.get_data()
    event_name = data.get('event_name')
    if message.text.lower() == 'quit':
        await state.clear()
        return
    host = await get_host_by_org_name(message.text, event_name)
    winner_id = await get_add_winner(host.user_id, event_name)
    if not winner_id:
        await safe_send_message(bot, message, 'В этом розыгрыше нет участников((')
        await state.clear()
        return
    winner = await get_user(winner_id)
    await safe_send_message(bot, message, f'@{winner.handler} - победитель розыгрыша от @{host.org_name}')
