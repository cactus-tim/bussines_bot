from datetime import datetime
from io import BytesIO
from typing import Union

import qrcode
from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.filters.command import CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile

from config.settings import TOKEN
from database.req import get_user, create_user_x_event_row, get_all_user_events, get_event, \
    get_reg_event, get_user_x_event_row, create_qr_code
from database.req.face_control import get_face_control
from handlers.error import safe_send_message
from handlers.utils.qr_utils import create_styled_qr_code
from keyboards.keyboards import face_checkout_kb, single_command_button_keyboard
from utils.base import is_valid_time_format

router = Router()

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(
        parse_mode=ParseMode.HTML,
    ),
)


@router.message(Command("check_qr"))
async def cmd_check_qr(message: Message, command: CommandObject):
    """Handle QR code verification via command."""
    if not command.args:
        await safe_send_message(bot, message, "Пожалуйста, укажите QR код после команды /check_qr")
        return

    hash_value = command.args
    if not hash_value.startswith('qr_'):
        await safe_send_message(bot, message, "Недействительный QR код")
        return

    try:
        # Split only on first two underscores to preserve event name
        parts = hash_value.split('_', 2)
        if len(parts) != 3:
            await safe_send_message(bot, message, "Недействительный QR код")
            return

        _, user_id, event_name = parts
        user_id = int(user_id)

        # Get user and event info
        user = await get_user(user_id)
        event = await get_event(event_name)

        if user == "not created" or event == "not created":
            await safe_send_message(bot, message, "Недействительный QR код")
            return

        # Check if user is registered for the event
        user_x_event = await get_user_x_event_row(user_id, event_name)
        if user_x_event == "not created":
            await safe_send_message(bot, message, "Пользователь не зарегистрирован на это мероприятие")
            return

        if user_x_event.status not in ['reg', 'been']:
            await safe_send_message(bot, message, "Пользователь не зарегистрирован на это мероприятие")
            return

        # Check if event is in progress
        if event.status != 'in_progress':
            await safe_send_message(bot, message, "Мероприятие не активно")
            return

        # Check if scanner is superuser
        scanner = await get_user(message.from_user.id)
        face_control = await get_face_control(message.from_user.id)
        if scanner.is_superuser or face_control != "not found":
            # Get user registration details
            reg_event = await get_reg_event(user_id)
            user_info = ""
            if reg_event:
                user_info = f"\nФИО: {reg_event.surname} {reg_event.name} {reg_event.fathername}\nТелефон: {reg_event.phone}"

            # Check if QR code was already used
            if user_x_event.status == 'been':
                await safe_send_message(bot, message,
                                        f"⚠️ Этот QR код уже был использован!\n\n"
                                        f"Пользователь: @{user.handler}{user_info}\n"
                                        f"Мероприятие: {event.desc}\n"
                                        f"Дата: {event.date}\n"
                                        f"Время: {event.time}\n"
                                        f"Место: {event.place}"
                                        )
                return

            # Show verification buttons
            await message.answer(
                f"Проверка QR кода:\n"
                f"Пользователь: @{user.handler}{user_info}\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}",
                reply_markup=face_checkout_kb(user_id, event_name)
            )
        else:
            # Check if the QR code belongs to the user who scanned it
            if user_id != message.from_user.id:
                await safe_send_message(bot, message,
                                        "⚠️ Это не ваш QR код! Вы можете сканировать только свои QR коды.")
                return

            # Check if QR code was already used
            if user_x_event.status == 'been':
                await safe_send_message(bot, message,
                                        f"Спасибо, что посетили это мероприятие!\n\n"
                                        f"Мероприятие: {event.desc}\n"
                                        f"Дата: {event.date}\n"
                                        f"Время: {event.time}\n"
                                        f"Место: {event.place}"
                                        )
                return

            # Show event info and verification buttons to regular users
            await message.answer(
                f"⚠️ ВАЖНО: Сохраните этот QR код!\n"
                f"Мероприятие: {event.desc}\n"
                f"Дата: {event.date}\n"
                f"Время: {event.time}\n"
                f"Место: {event.place}\n"
                f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!",
            )

    except (ValueError, IndexError) as e:
        print(f"QR code validation error: {e}")
        await safe_send_message(bot, message, "Недействительный QR код")
        return


@router.message(Command("my_qr"))
async def cmd_my_qr(message: Message):
    """Handle /my_qr command to get QR code for event registration."""
    await handle_qr_request(message)


@router.message(F.text == "Получить QR-код")
async def handle_qr_button(message: Message):
    """Handle QR code button press."""
    await handle_qr_request(message)


async def handle_qr_request(message: Message):
    """Common handler for QR code requests from both command and button."""
    user = await get_user(message.from_user.id)
    if user == "not created":
        await safe_send_message(bot, message, "Вы не зарегистрированы в боте")
        return

    # Get all user's events
    events = await get_all_user_events(message.from_user.id)
    if not events:
        await safe_send_message(bot, message, "У вас нет активных регистраций на мероприятия")
        return

    current_time = datetime.now()

    # Separate future and past events
    future_events = []
    past_events = []

    for event in events:
        try:
            # Extract date from event name (format: eventDD_MM_YY)
            date_parts = event.name.replace('event', '').split('_')
            if len(date_parts) == 3:
                day = int(date_parts[0])
                month = int(date_parts[1])
                year = 2000 + int(date_parts[2])  # Convert YY to YYYY

                # Parse time if available and valid
                hour, minute = 0, 0
                if event.time and is_valid_time_format(event.time):
                    hour, minute = map(int, event.time.split(':'))

                event_date = datetime(year, month, day, hour, minute)

                if event_date > current_time:
                    future_events.append(event)
                else:
                    past_events.append(event)
        except (ValueError, IndexError) as e:
            print(f"Error parsing date for event {event.name}: {e}")
            continue

    # Choose the nearest event
    target_event = None
    if future_events:
        # If there are future events, take the nearest one
        target_event = min(future_events,
                           key=lambda x: datetime.strptime(f"{x.name.replace('event', '')}", "%d_%m_20%y"))
    elif past_events:
        # If no future events, take the most recent past event
        target_event = max(past_events, key=lambda x: datetime.strptime(f"{x.name.replace('event', '')}", "%d_%m_20%y"))

    if target_event:
        # Check if user has already attended the event
        user_x_event = await get_user_x_event_row(message.from_user.id, target_event.name)
        if user_x_event and user_x_event.status == 'been':
            bot_username = (await bot.get_me()).username
            qr_data = f"https://t.me/{bot_username}?start=qr_{message.from_user.id}_{target_event.name}"
            qr_image = create_styled_qr_code(qr_data)

            # Create QR code record
            await create_qr_code(message.from_user.id, target_event.name)

            # Save QR code to a temporary file
            temp_file = "temp_qr.png"
            with open(temp_file, "wb") as f:
                f.write(qr_image.getvalue())

            await message.answer_photo(
                photo=FSInputFile(temp_file),
                caption=f"Спасибо, что посетили это мероприятие!\n\n"
                        f"Название: {target_event.desc}\n"
                        f"Дата: {target_event.date}\n"
                        f"Время: {target_event.time}\n"
                        f"Место: {target_event.place}"
            )
            return

        bot_username = (await bot.get_me()).username
        qr_data = f"https://t.me/{bot_username}?start=qr_{message.from_user.id}_{target_event.name}"
        qr_image = create_styled_qr_code(qr_data)

        # Create QR code record
        await create_qr_code(message.from_user.id, target_event.name)

        # Save QR code to a temporary file
        temp_file = "temp_qr.png"
        with open(temp_file, "wb") as f:
            f.write(qr_image.getvalue())

        try:
            # Send QR code with detailed caption
            await message.answer_photo(
                photo=FSInputFile(temp_file),
                caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                        f"Это ваш пропуск на мероприятие:\n"
                        f"Название: {target_event.desc}\n"
                        f"Дата: {target_event.date}\n"
                        f"Время: {target_event.time}\n"
                        f"Место: {target_event.place}\n\n"
                        f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
            )
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
    else:
        await safe_send_message(bot, message, "Не удалось найти подходящее мероприятие")


@router.callback_query(lambda c: c.data.startswith("qr_"))
async def process_qr_event_selection(callback: CallbackQuery):
    """Handle event selection for QR code generation."""
    try:
        event_name = callback.data
        event = await get_event(event_name.replace('qr_', ''))

        if event == "not created":
            await callback.answer("Мероприятие не найдено")
            return

        # Verify that user is registered for this event
        user_x_event = await get_user_x_event_row(callback.from_user.id, event_name)
        if user_x_event == "not created":
            await callback.answer("Вы не зарегистрированы на это мероприятие")
            return

        # Generate QR code
        bot_username = (await bot.get_me()).username
        qr_data = f"https://t.me/{bot_username}?start=qr_{callback.from_user.id}_{event_name}"
        qr_image = create_styled_qr_code(qr_data)

        # Create QR code record
        await create_qr_code(callback.from_user.id, event_name)

        # Save QR code to a temporary file
        temp_file = "temp_qr.png"
        with open(temp_file, "wb") as f:
            f.write(qr_image.getvalue())

        try:
            # Send QR code with detailed caption
            await callback.message.answer_photo(
                photo=FSInputFile(temp_file),
                caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                        f"Это ваш пропуск на мероприятие:\n"
                        f"Название: {event.desc}\n"
                        f"Дата: {event.date}\n"
                        f"Время: {event.time}\n"
                        f"Место: {event.place}\n\n"
                        f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
            )
            # Delete the keyboard message
            await callback.message.delete()
        finally:
            # Clean up temporary file
            import os
            if os.path.exists(temp_file):
                os.remove(temp_file)
    except Exception as e:
        print(f"QR code generation error: {e}")
        await callback.answer("Произошла ошибка при генерации QR кода")


@router.callback_query(F.data == "yes")
async def process_reg_yes(callback: CallbackQuery, state: FSMContext):
    """Handle event registration confirmation."""
    data = await state.get_data()
    event_name = data.get("name")

    # Create registration
    await create_user_x_event_row(callback.from_user.id, event_name, callback.from_user.username)
    event = await get_event(event_name)

    # Generate and send QR code
    bot_username = (await bot.get_me()).username
    qr_data = f"https://t.me/{bot_username}?start=qr_{callback.from_user.id}_{event_name}"
    qr_image = create_styled_qr_code(qr_data)
    await create_qr_code(callback.from_user.id, event_name)

    # Save QR code to a temporary file
    temp_file = "temp_qr.png"
    with open(temp_file, "wb") as f:
        f.write(qr_image.getvalue())

    try:
        await callback.message.answer_photo(
            photo=FSInputFile(temp_file),
            caption=f"Вы успешно зарегистрировались на мероприятие!\n\n"
                    f"Название: {event.desc}\n"
                    f"Дата: {event.date}\n"
                    f"Время: {event.time}\n"
                    f"Место: {event.place}\n\n"
                    f"Покажите этот QR код при входе на мероприятие."
        )
    finally:
        # Clean up temporary file
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)

    await state.clear()


async def send_event_qr_code(user_id: int, event_name: str, message: Union[Message, CallbackQuery], state: FSMContext):
    """Send QR code for event registration."""
    try:
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(event_name)
        qr.make(fit=True)
        qr_image = qr.make_image(fill_color="black", back_color="white")

        # Save QR code to bytes
        qr_bytes = BytesIO()
        qr_image.save(qr_bytes, format='PNG')
        qr_bytes.seek(0)

        # Send QR code
        if isinstance(message, CallbackQuery):
            await message.message.answer_photo(
                photo=qr_bytes,
                caption=f"Ваш QR-код для мероприятия {event_name}",
                reply_markup=single_command_button_keyboard()
            )
            await message.answer()  # Отвечаем на callback query
        else:
            await message.answer_photo(
                photo=qr_bytes,
                caption=f"Ваш QR-код для мероприятия {event_name}",
                reply_markup=single_command_button_keyboard()
            )

        # Clear state
        await state.clear()

    except Exception as e:
        print(f"Error generating QR code: {e}")
        if isinstance(message, CallbackQuery):
            await message.message.answer("Произошла ошибка при генерации QR-кода")
            await message.answer()  # Отвечаем на callback query
        else:
            await message.answer("Произошла ошибка при генерации QR-кода")
