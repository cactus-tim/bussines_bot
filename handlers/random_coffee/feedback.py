"""
Random Coffee Feedback

Feedback handlers for Random Coffee functionality and FSM interactions.
"""

# --------------------------------------------------------------------------------

from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RandomCoffeeFeedback
from handlers.states import FeedbackStates
from keyboards.random_coffee.base import get_feedback_keyboard

# --------------------------------------------------------------------------------

router = Router()

# --------------------------------------------------------------------------------

@router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext, session: AsyncSession):
    """
    Handle the /feedback command to start feedback collection.

    Args:
        message (Message): Incoming message from the user.
        state (FSMContext): Finite state machine context.
        session (AsyncSession): SQLAlchemy async session.

    Returns:
        None
    """
    query = text("""
                 SELECT *
                 FROM random_coffee_pairs
                 WHERE (user1_id = :user_id OR user2_id = :user_id)
                   AND week_start = (SELECT MAX(week_start)
                                     FROM random_coffee_pairs
                                     WHERE user1_id = :user_id
                                        OR user2_id = :user_id)
                 """)
    result = await session.execute(query, {"user_id": message.from_user.id})

    pair = result.first()

    if not pair:
        await message.answer(
            "У вас пока нет встреч для оценки. "
            "Оценить встречу можно будет после того, как она состоится."
        )
        return

    existing_feedback = await session.scalar(
        select(RandomCoffeeFeedback)
        .where(
            RandomCoffeeFeedback.pair_id == pair.id,
            RandomCoffeeFeedback.user_id == message.from_user.id
        )
    )

    if existing_feedback:
        await message.answer(
            "Вы уже оставили отзыв об этой встрече."
        )
        return

    await message.answer(
        "Оцените вашу встречу по шкале от 1 до 5:",
        reply_markup=get_feedback_keyboard()
    )
    await state.set_state(FeedbackStates.waiting_for_rating)

# --------------------------------------------------------------------------------

@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: CallbackQuery, state: FSMContext):
    """
    Process the rating value selected by the user.

    Args:
        callback (CallbackQuery): Callback containing rating data.
        state (FSMContext): Finite state machine context.

    Returns:
        None
    """
    rating = int(callback.data.split("_")[1])
    await state.update_data(rating=rating)

    await callback.message.answer(
        "Хотите оставить комментарий к оценке? "
        "Если нет, просто напишите 'нет'."
    )
    await state.set_state(FeedbackStates.waiting_for_comment)
    await callback.answer()

# --------------------------------------------------------------------------------

@router.message(FeedbackStates.waiting_for_comment)
async def process_comment(message: Message, state: FSMContext, session: AsyncSession):
    """
    Process and save the feedback comment and rating.

    Args:
        message (Message): Incoming message with optional comment.
        state (FSMContext): Finite state machine context.
        session (AsyncSession): SQLAlchemy async session.

    Returns:
        None
    """
    data = await state.get_data()
    rating = data["rating"]
    comment = None if message.text.lower() == "нет" else message.text

    query = text("""
                 SELECT *
                 FROM random_coffee_pairs
                 WHERE (user1_id = :user_id OR user2_id = :user_id)
                   AND week_start = (SELECT MAX(week_start)
                                     FROM random_coffee_pairs
                                     WHERE user1_id = :user_id
                                        OR user2_id = :user_id)
                 """)
    result = await session.execute(query, {"user_id": message.from_user.id})

    pair = result.first()

    feedback = RandomCoffeeFeedback(
        pair_id=pair.id,
        user_id=message.from_user.id,
        rating=rating,
        comment=comment,
        created_at=datetime.now().isoformat()
    )
    session.add(feedback)
    await session.commit()

    await message.answer(
        "Спасибо за ваш отзыв! "
        "Это поможет нам сделать Random Coffee еще лучше."
    )
    await state.clear()
