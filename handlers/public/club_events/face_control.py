"""
QR Verification Handler
Handles QR verification and user admission to club_events.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import CallbackQuery

from config.settings import TOKEN
from database.req import (
    get_user, get_event, update_user_x_event_row_status,
    get_reg_event, get_user_x_event_row, get_all_hosts_in_event_ids,
    add_money, one_more_event, add_referal_cnt, update_strick
)
from handlers.error import safe_send_message

# --------------------------------------------------------------------------------

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML),
)


# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("verify_"))
async def process_verification(callback: CallbackQuery):
    """
    Handle QR code verification by admin.

    Args:
        callback (CallbackQuery): Callback query triggered by admin verification.

    Returns:
        None
    """
    try:
        parts = callback.data.split('_')

        if len(parts) < 4:
            await callback.answer("Неверный формат данных")
            return

        user_id = int(parts[1])
        action = parts[-1]
        event_name = '_'.join(parts[2:-1])

        user = await get_user(user_id)
        event = await get_event(event_name)

        if user == "not created" or event == "not created":
            await callback.answer("Пользователь или мероприятие не найдены")
            return

        reg_event = await get_reg_event(user_id)
        user_info = ""
        if reg_event:
            user_info = (
                f"\nФИО: {reg_event.surname} {reg_event.name} {reg_event.fathername}\n"
                f"Телефон: {reg_event.phone}"
            )

        if action == "allow":
            await update_user_x_event_row_status(user_id, event_name, 'been')
            await add_money(user_id, 1)
            await one_more_event(user_id)
            await update_strick(user_id)

            await callback.answer("✅ Пользователь успешно пропущен")

            await bot.send_message(
                user_id,
                f"Ваш QR код был успешно отсканирован на мероприятии {event.desc}!"
            )

            user_x_event = await get_user_x_event_row(user_id, event_name)
            if user_x_event != "not created" and user_x_event.first_contact != '0':
                ref_giver = await get_user(int(user_x_event.first_contact))
                if ref_giver != "not created":
                    hosts_ids = await get_all_hosts_in_event_ids(event_name)
                    if (not hosts_ids or ref_giver.id not in hosts_ids):
                        await safe_send_message(
                            bot,
                            ref_giver.id,
                            f'Вы получили 2 монетки за то что приглашенный вами человек '
                            f'@{user.handler} посетил событие!'
                        )
                        await add_money(ref_giver.id, 2)
                        await add_referal_cnt(ref_giver.id)
                        await safe_send_message(
                            bot,
                            user_id,
                            f'Вы получили монетку за то что вы зарегистрировались по '
                            f'реферальной ссылке @{ref_giver.handler}!'
                        )
                        await add_money(user_id, 1)

            await callback.message.edit_text(
                f"✅ Пользователь пропущен:\n"
                f"Пользователь: @{user.handler}{user_info}\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}"
            )
        else:
            await callback.answer("❌ Пользователь не пропущен")
            await callback.message.edit_text(
                f"❌ Пользователь не пропущен:\n"
                f"Пользователь: @{user.handler}{user_info}\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}"
            )

    except Exception as e:
        print(f"Verification error: {e}")
        await callback.answer("Произошла ошибка при обработке верификации")
