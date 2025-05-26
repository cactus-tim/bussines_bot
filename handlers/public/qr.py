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
from handlers.error import safe_send_message
from handlers.utils.base import get_bot_username
from handlers.utils.qr_utils import create_styled_qr_code
from keyboards.keyboards import get_ref_ikb, face_checkout_kb, choose_event_for_qr

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
        if scanner.is_superuser:
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

            # Show event info to regular users
            await safe_send_message(bot, message,
                                    f"Информация о мероприятии:\n"
                                    f"Название: {event.desc}\n"
                                    f"Дата: {event.date}\n"
                                    f"Время: {event.time}\n"
                                    f"Место: {event.place}"
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

    await safe_send_message(bot, message, "Выберите мероприятие, для которого хотите получить QR код:",
                            reply_markup=choose_event_for_qr(events))


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
        bot_username = await get_bot_username()
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


async def send_event_qr_code(user_id: int, event_name: str, message: Message | CallbackQuery, state: FSMContext = None):
    """Helper function to generate and send QR code for event registration."""
    event = await get_event(event_name)
    await create_user_x_event_row(user_id, event_name, message.from_user.username)
    bot_username = (await bot.get_me()).username
    qr_data = f"https://t.me/{bot_username}?start=qr_{user_id}_{event_name}"
    qr_image = create_styled_qr_code(qr_data)
    await create_qr_code(user_id, event_name)

    temp_file = "temp_qr.png"
    with open(temp_file, "wb") as f:
        f.write(qr_image.getvalue())

    try:
        await safe_send_message(bot, message,
                                f"Мы вас ждем на мероприятии \"{event.desc}\", которое пройдет {event.date} в {event.time}\n"
                                f"Место проведение - {event.place}",
                                reply_markup=get_ref_ikb(event_name)
                                )
        await message.answer_photo(
            photo=FSInputFile(temp_file),
            caption=f"⚠️ ВАЖНО: Сохраните этот QR код!\n\n"
                    f"Это ваш пропуск на мероприятие:\n"
                    f"Название: {event.desc}\n"
                    f"Дата: {event.date}\n"
                    f"Время: {event.time}\n"
                    f"Место: {event.place}\n\n"
                    f"Покажите этот QR код при входе на мероприятие. Без него вас могут не пропустить!"
        )
    finally:
        import os
        if os.path.exists(temp_file):
            os.remove(temp_file)

    if state:
        await state.clear()


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
        user_x_event = await get_user_x_event_row(callback.from_user.id, event_name.replace('qr_', ''))
        if user_x_event == "not created":
            await callback.answer("Вы не зарегистрированы на это мероприятие")
            return

        # Generate QR code
        bot_username = (await bot.get_me()).username
        qr_data = f"https://t.me/{bot_username}?start=qr_{callback.from_user.id}_{event_name.replace('qr_', '')}"
        qr_image = create_styled_qr_code(qr_data)

        # Create QR code record
        await create_qr_code(callback.from_user.id, event_name.replace('qr_', ''))

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
