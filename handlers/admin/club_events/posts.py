"""
Send Post Router
Handles admin post distribution to Telegram users.
"""

# --------------------------------------------------------------------------------

from aiogram import Router, F, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from config.settings import TOKEN
from config.texts.admin import EVENT_END_FEEDBACK
from database.req import (
    get_user, get_all_events, get_users_tg_id_in_event,
    get_users_unreg_tg_id, get_users_tg_id
)
from handlers.error import safe_send_message
from handlers.states import PostState
from keyboards import (
    post_ev_target, main_reply_keyboard,
    post_target, unreg_yes_no_link_ikb, yes_no_link_ikb, link_ikb
)

# --------------------------------------------------------------------------------

router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# --------------------------------------------------------------------------------

@router.message(Command("send_post"))
async def cmd_send_post(message: Message):
    """
    Entry point to start the post sending process.

    Args:
        message (Message): Incoming message from admin.

    Returns:
        None
    """
    user = await get_user(message.from_user.id)
    if not user.is_superuser:
        return
    await safe_send_message(
        bot,
        message,
        text="Выберете кому вы хотите отправить пост",
        reply_markup=post_target()
    )

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "cancel")
async def cancel(callback: CallbackQuery, state: FSMContext):
    """
    Cancels current FSM context and deletes previous messages.

    Args:
        callback (CallbackQuery): Callback query from user.
        state (FSMContext): Current FSM context.

    Returns:
        None
    """
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.delete_message(callback.from_user.id, callback.message.message_id - 1)
    await state.clear()
    return

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "post_to_unreg")
async def choose_event(callback: CallbackQuery, state: FSMContext):
    """
    Starts process of choosing an event for unregistered users.

    Args:
        callback (CallbackQuery): Callback query from user.
        state (FSMContext): FSM context to store selected event.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(
        bot,
        callback,
        text="Выберете событие:\n\nДля отмены введите quit",
        reply_markup=post_ev_target(events)
    )
    await state.set_state(PostState.waiting_for_post_to_ev_ev_unreg)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_ev_ev_unreg)
async def mb_add_link_unreg(message: Message, state: FSMContext):
    """
    Asks whether to add a link to the post.

    Args:
        message (Message): Incoming message with event name.
        state (FSMContext): FSM context to store event name.

    Returns:
        None
    """
    await state.update_data({'event_name': message.text})
    await safe_send_message(
        bot,
        message,
        "Хочешь добавить к посту кнопку с ссылкой?",
        unreg_yes_no_link_ikb()
    )

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "unreg_link_no")
async def link_no_unreg(callback: CallbackQuery, state: FSMContext):
    """
    Continues posting without link.

    Args:
        callback (CallbackQuery): Callback query from user.
        state (FSMContext): FSM context to update flag.

    Returns:
        None
    """
    await state.update_data({'flag': False})
    await safe_send_message(
        bot,
        callback,
        text="Отправьте мне пост (текст, фото или видео)\n\nДля отмены введите quit"
    )
    await state.set_state(PostState.waiting_for_post_to_all_media_unreg)

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "unreg_link_yes")
async def link_yes_unreg(callback: CallbackQuery, state: FSMContext):
    """
    Prompts user to send a link.

    Args:
        callback (CallbackQuery): Callback query from user.
        state (FSMContext): FSM context to transition.

    Returns:
        None
    """
    await safe_send_message(
        bot,
        callback,
        text="Отправь мне ссылку\n\nДля отмены введите quit"
    )
    await state.set_state(PostState.waiting_for_post_to_all_text05_unreg)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_all_media_unreg)
async def process_post_to_all_media_unreg(message: Message, state: FSMContext):
    """
    Processes and sends post to unregistered users.

    Args:
        message (Message): Message containing post content.
        state (FSMContext): FSM context with event and post data.

    Returns:
        None
    """
    if message.text and message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return

    data = await state.get_data()
    event_name = data.get('event_name')
    flag = data.get('flag', False)
    user_ids = await get_users_unreg_tg_id(event_name)

    if not user_ids:
        await safe_send_message(
            bot,
            message,
            text="У вас нет пользователей((",
            reply_markup=main_reply_keyboard()
        )
        return

    status_message = await safe_send_message(
        bot,
        message,
        f"🚀 Начинаю рассылку для незарегистрированных пользователей события {event_name}...\n"
        f"Всего получателей: {len(user_ids)}\nОтправлено: 0\nОшибок: 0"
    )

    reply_markup = None
    if flag:
        link = data.get('link')
        text = data.get('text')
        reply_markup = link_ikb(text, link)

    failed_users = []
    success_count = 0
    total = len(user_ids)

    async def update_status(text: str):
        """
        Updates or replaces status message.

        Args:
            text (str): Text to display in the status message.

        Returns:
            None
        """
        nonlocal status_message
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_message.message_id,
                text=text
            )
        except Exception:
            try:
                await bot.delete_message(message.chat.id, status_message.message_id)
            except Exception:
                pass
            status_message = await safe_send_message(bot, message, text)

    for i, user_id in enumerate(user_ids, 1):
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    reply_markup=reply_markup or main_reply_keyboard()
                )
            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption,
                    reply_markup=reply_markup or main_reply_keyboard()
                )
            else:
                await safe_send_message(
                    bot,
                    user_id,
                    text=message.text,
                    reply_markup=reply_markup or main_reply_keyboard()
                )
            success_count += 1

            if i % 10 == 0 or i == total:
                await update_status(
                    f"📨 Рассылка в процессе...\n"
                    f"Событие: {event_name}\n"
                    f"Всего получателей: {total}\n"
                    f"Отправлено: {success_count}\n"
                    f"Ошибок: {len(failed_users)}\n"
                    f"Прогресс: {i}/{total} ({int(i / total * 100)}%)"
                )
        except Exception:
            failed_users.append(user_id)
            continue

    await update_status(
        f"✅ Рассылка завершена!\n"
        f"Событие: {event_name}\n"
        f"Всего получателей: {total}\n"
        f"Успешно отправлено: {success_count}\n"
        f"Ошибок: {len(failed_users)}"
    )

    await state.clear()

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "post_to_all")
async def mb_add_link(callback: CallbackQuery, state: FSMContext):
    """
    Asks whether to add a link before posting to all users.

    Args:
        callback (CallbackQuery): Callback query from admin.
        state (FSMContext): FSM context to store user choice.

    Returns:
        None
    """
    await safe_send_message(
        bot,
        callback,
        "Хочешь добавить к посту кнопку с ссылкой?",
        yes_no_link_ikb()
    )


# --------------------------------------------------------------------------------

@router.callback_query(F.data == "link_no")
async def link_no(callback: CallbackQuery, state: FSMContext):
    """
    Continues posting without a link.

    Args:
        callback (CallbackQuery): User interaction callback.
        state (FSMContext): State machine context.

    Returns:
        None
    """
    await state.update_data({'flag': False})
    await safe_send_message(
        bot,
        callback,
        text="Отправьте мне пост (текст, фото или видео)\n\nДля отмены введите quit"
    )
    await state.set_state(PostState.waiting_for_post_to_all_media)

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "link_yes")
async def link_yes(callback: CallbackQuery, state: FSMContext):
    """
    Starts flow to add a link button.

    Args:
        callback (CallbackQuery): User interaction callback.
        state (FSMContext): State machine context.

    Returns:
        None
    """
    await safe_send_message(
        bot,
        callback,
        text="Отправь мне ссылку\n\nДля отмены введите quit"
    )
    await state.set_state(PostState.waiting_for_post_to_all_text05)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_all_media)
async def process_post_to_all_media(message: Message, state: FSMContext):
    """
    Sends the prepared post to all users.

    Args:
        message (Message): Message with content.
        state (FSMContext): Context with link flag and data.

    Returns:
        None
    """
    if message.text and message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return

    user_ids = await get_users_tg_id()
    if not user_ids:
        await safe_send_message(
            bot,
            message,
            text="У вас нет пользователей((",
            reply_markup=main_reply_keyboard()
        )
        return

    status_message = await safe_send_message(
        bot,
        message,
        f"🚀 Начинаю рассылку...\nВсего получателей: {len(user_ids)}\n"
        f"Отправлено: 0\nОшибок: 0"
    )

    data = await state.get_data()
    flag = data.get('flag', False)
    reply_markup = None
    if flag:
        link = data.get('link')
        text = data.get('text')
        reply_markup = link_ikb(text, link)

    failed_users = []
    success_count = 0
    total = len(user_ids)

    async def update_status(text: str):
        """
        Updates progress status in the chat.

        Args:
            text (str): Progress message.

        Returns:
            None
        """
        nonlocal status_message
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_message.message_id,
                text=text
            )
        except Exception:
            try:
                await bot.delete_message(message.chat.id, status_message.message_id)
            except Exception:
                pass
            status_message = await safe_send_message(bot, message, text)

    for i, user_id in enumerate(user_ids, 1):
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    reply_markup=reply_markup or main_reply_keyboard()
                )
            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption,
                    reply_markup=reply_markup or main_reply_keyboard()
                )
            else:
                await safe_send_message(
                    bot,
                    user_id,
                    text=message.text,
                    reply_markup=reply_markup or main_reply_keyboard()
                )
            success_count += 1

            if i % 10 == 0 or i == total:
                await update_status(
                    f"📨 Рассылка в процессе...\n"
                    f"Всего получателей: {total}\n"
                    f"Отправлено: {success_count}\n"
                    f"Ошибок: {len(failed_users)}\n"
                    f"Прогресс: {i}/{total} ({int(i / total * 100)}%)"
                )

        except Exception:
            failed_users.append(user_id)
            continue

    await update_status(
        f"✅ Рассылка завершена!\n"
        f"Всего получателей: {total}\n"
        f"Успешно отправлено: {success_count}\n"
        f"Ошибок: {len(failed_users)}"
    )

    await state.clear()

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_all_text05)
async def cmd_post_to_all(message: Message, state: FSMContext):
    """
    Receives the link and asks for button text.

    Args:
        message (Message): Message with the link.
        state (FSMContext): Context to store link.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await state.update_data({'link': message.text, 'flag': True})
    await safe_send_message(
        bot,
        message,
        text="Отправь надпись на кнопке\n\nДля отмены введите quit"
    )
    await state.set_state(PostState.waiting_for_post_to_all_text1)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_all_text1)
async def cmd_post_to_all(message: Message, state: FSMContext):
    """
    Receives button text and moves to media collection.

    Args:
        message (Message): Message with button text.
        state (FSMContext): Context to update button label.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await state.update_data({'text': message.text})
    await safe_send_message(
        bot,
        message,
        text="Отправьте мне пост (текст, фото или видео)\n\nДля отмены введите quit"
    )
    await state.set_state(PostState.waiting_for_post_to_all_media)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_all_text)
async def process_post_to_all(message: Message, state: FSMContext):
    """
    Sends post with or without button to all users.

    Args:
        message (Message): Post content.
        state (FSMContext): FSM state with post options.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return

    user_ids = await get_users_tg_id()
    data = await state.get_data()
    flag = data.get('flag')
    if flag:
        link = data.get('link')
        text = data.get('text')

    if not user_ids:
        await safe_send_message(
            bot,
            message,
            text="У вас нет пользователей((",
            reply_markup=main_reply_keyboard()
        )
        return

    for user_id in user_ids:
        await safe_send_message(
            bot,
            user_id,
            text=message.text,
            reply_markup=(main_reply_keyboard() if not flag else link_ikb(text, link))
        )

    await safe_send_message(bot, message, "Готово", reply_markup=main_reply_keyboard())
    await state.clear()

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "post_to_ev")
async def cmd_post_to_ev(callback: CallbackQuery, state: FSMContext):
    """
    Starts event-specific post distribution.

    Args:
        callback (CallbackQuery): Callback from user.
        state (FSMContext): FSM state for event flow.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(
        bot,
        callback,
        text="Выберете событие:\n\nДля отмены введите quit",
        reply_markup=post_ev_target(events)
    )
    await state.set_state(PostState.waiting_for_post_to_ev_ev)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_ev_ev)
async def pre_process_post_to_ev(message: Message, state: FSMContext):
    """
    Gets event name and requests post content.

    Args:
        message (Message): Message with event name.
        state (FSMContext): FSM state to save event.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await safe_send_message(
        bot,
        message,
        text="Отправьте мне пост (текст, фото или видео)\n\nДля отмены введите quit"
    )
    await state.update_data(event_name=message.text)
    await state.set_state(PostState.waiting_for_post_to_ev_media)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_to_ev_media)
async def process_post_to_ev_media(message: Message, state: FSMContext):
    """
    Sends a post to users registered in a specific event.

    Args:
        message (Message): Incoming post message.
        state (FSMContext): FSM context with event data.

    Returns:
        None
    """
    if message.text and message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return

    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(
            bot,
            message,
            text="У вас нет пользователей принявших участие в этом событии",
            reply_markup=main_reply_keyboard()
        )
        return

    status_message = await safe_send_message(
        bot,
        message,
        f"🚀 Начинаю рассылку для события {event_name}...\n"
        f"Всего получателей: {len(user_ids)}\nОтправлено: 0\nОшибок: 0"
    )

    failed_users = []
    success_count = 0
    total = len(user_ids)

    async def update_status(text: str):
        """
        Updates or replaces the status message in the chat.

        Args:
            text (str): Text content for update.

        Returns:
            None
        """
        nonlocal status_message
        try:
            await bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=status_message.message_id,
                text=text
            )
        except Exception:
            try:
                await bot.delete_message(message.chat.id, status_message.message_id)
            except Exception:
                pass
            status_message = await safe_send_message(bot, message, text)

    for i, user_id in enumerate(user_ids, 1):
        try:
            if message.photo:
                await bot.send_photo(
                    chat_id=user_id,
                    photo=message.photo[-1].file_id,
                    caption=message.caption,
                    reply_markup=main_reply_keyboard()
                )
            elif message.video:
                await bot.send_video(
                    chat_id=user_id,
                    video=message.video.file_id,
                    caption=message.caption,
                    reply_markup=main_reply_keyboard()
                )
            else:
                await safe_send_message(
                    bot,
                    user_id,
                    text=message.text,
                    reply_markup=main_reply_keyboard()
                )
            success_count += 1

            if i % 10 == 0 or i == total:
                await update_status(
                    f"📨 Рассылка в процессе...\n"
                    f"Событие: {event_name}\n"
                    f"Всего получателей: {total}\n"
                    f"Отправлено: {success_count}\n"
                    f"Ошибок: {len(failed_users)}\n"
                    f"Прогресс: {i}/{total} ({int(i / total * 100)}%)"
                )
        except Exception:
            failed_users.append(user_id)
            continue

    await update_status(
        f"✅ Рассылка завершена!\n"
        f"Событие: {event_name}\n"
        f"Всего получателей: {total}\n"
        f"Успешно отправлено: {success_count}\n"
        f"Ошибок: {len(failed_users)}"
    )

    await state.clear()

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "post_wth_op_to_ev")
async def cmd_post_to_ev(callback: CallbackQuery, state: FSMContext):
    """
    Starts flow to send a post with feedback form link.

    Args:
        callback (CallbackQuery): Callback from admin.
        state (FSMContext): FSM context for storing event.

    Returns:
        None
    """
    events = await get_all_events()
    if not events:
        await safe_send_message(bot, callback, text="У вас нет событий")
        return
    await safe_send_message(
        bot,
        callback,
        text="Выберете событие:\n\nДля отмены введите quit",
        reply_markup=post_ev_target(events)
    )
    await state.set_state(PostState.waiting_for_post_wth_op_to_ev_ev)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_wth_op_to_ev_ev)
async def pre_process_post_to_ev(message: Message, state: FSMContext):
    """
    Receives event name and requests Google Form link.

    Args:
        message (Message): Message with event name.
        state (FSMContext): FSM context to store event.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return
    await safe_send_message(
        bot,
        message,
        text="Отправьте мне ссылку на гугл-форму\n\nДля отмены введите quit"
    )
    await state.update_data(event_name=message.text)
    await state.set_state(PostState.waiting_for_post_wth_op_to_ev_text)

# --------------------------------------------------------------------------------

@router.message(PostState.waiting_for_post_wth_op_to_ev_text)
async def process_post_to_wth_op_to_ev(message: Message, state: FSMContext):
    """
    Sends feedback form link to users in selected event.

    Args:
        message (Message): Message containing Google Form link.
        state (FSMContext): FSM context containing event.

    Returns:
        None
    """
    if message.text.lower() == 'quit':
        await safe_send_message(bot, message, 'Вы вышли')
        await state.clear()
        return

    data = await state.get_data()
    event_name = data.get("event_name")
    user_ids = await get_users_tg_id_in_event(event_name)
    if not user_ids:
        await safe_send_message(
            bot,
            message,
            text="У вас нет пользователей принявших участие в этом событии",
            reply_markup=main_reply_keyboard()
        )
        return

    for user_id in user_ids:
        await safe_send_message(
            bot,
            user_id,
            text=EVENT_END_FEEDBACK,
            reply_markup=link_ikb('Форма обратной связи', message.text)
        )

    await safe_send_message(bot, message, "Готово", reply_markup=main_reply_keyboard())
    await state.clear()
