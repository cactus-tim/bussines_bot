"""
Weekly Participation

Handlers for managing weekly Random Coffee participation.
"""

# --------------------------------------------------------------------------------

import logging
from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import RandomCoffeeWeek, RandomCoffeePair
from database.req.random_coffee import get_user_profile
from handlers.random_coffee.profile import cmd_edit_profile
from utils.random_coffee.helpers import get_week_start_date

# --------------------------------------------------------------------------------

router = Router()
logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "participate_yes")
async def handle_participation_yes(callback: CallbackQuery, session: AsyncSession):
    """
    Handle user agreement to participate in this week's Random Coffee.

    Args:
        callback (CallbackQuery): Telegram callback query.
        session (AsyncSession): SQLAlchemy database session.

    Returns:
        None
    """
    try:
        profile = await get_user_profile(session, callback.from_user.id)
        if not profile:
            await callback.message.answer(
                "У вас еще нет анкеты Random Coffee. "
                "Используйте /random_coffee для создания анкеты."
            )
            return

        week_start = get_week_start_date()
        existing_participation = await session.scalar(
            select(RandomCoffeeWeek).where(
                RandomCoffeeWeek.user_id == callback.from_user.id,
                RandomCoffeeWeek.week_start == week_start.isoformat()
            )
        )

        if existing_participation:
            if existing_participation.is_participating:
                await callback.message.answer(
                    "Вы уже зарегистрированы на участие в Random Coffee на этой неделе."
                )
                return
            existing_participation.is_participating = True
            existing_participation.created_at = datetime.now().isoformat()
        else:
            participation = RandomCoffeeWeek(
                user_id=callback.from_user.id,
                week_start=week_start.isoformat(),
                is_participating=True,
                created_at=datetime.now().isoformat()
            )
            session.add(participation)

        await session.commit()

        await callback.message.answer(
            "Отлично! Вы будете участвовать в Random Coffee на следующей неделе. "
            "Мы сообщим вам о вашем собеседнике в понедельник."
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_participation_yes: {e}")
        await callback.message.answer(
            "Произошла ошибка при регистрации участия. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "participate_no")
async def handle_participation_no(callback: CallbackQuery, session: AsyncSession):
    """
    Handle user refusal to participate in this week's Random Coffee.

    Args:
        callback (CallbackQuery): Telegram callback query.
        session (AsyncSession): SQLAlchemy database session.

    Returns:
        None
    """
    try:
        profile = await get_user_profile(session, callback.from_user.id)
        if not profile:
            await callback.message.answer(
                "У вас еще нет анкеты Random Coffee. "
                "Используйте /random_coffee для создания анкеты."
            )
            return

        week_start = get_week_start_date()
        existing_participation = await session.scalar(
            select(RandomCoffeeWeek).where(
                RandomCoffeeWeek.user_id == callback.from_user.id,
                RandomCoffeeWeek.week_start == week_start.isoformat()
            )
        )

        if existing_participation:
            if not existing_participation.is_participating:
                await callback.message.answer(
                    "Хорошо, пропускаем вас на этой неделе. "
                    "Надеемся увидеть вас в следующий раз!"
                )
                return
            existing_participation.is_participating = False
            existing_participation.created_at = datetime.now().isoformat()
        else:
            participation = RandomCoffeeWeek(
                user_id=callback.from_user.id,
                week_start=week_start.isoformat(),
                is_participating=False,
                created_at=datetime.now().isoformat()
            )
            session.add(participation)

        await session.commit()

        await callback.message.answer(
            "Хорошо, пропускаем вас на этой неделе. "
            "Надеемся увидеть вас в следующий раз!"
        )
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_participation_no: {e}")
        await callback.message.answer(
            "Произошла ошибка при отмене участия. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

# --------------------------------------------------------------------------------

@router.callback_query(F.data == "view_profile")
async def handle_view_profile(callback: CallbackQuery, session: AsyncSession):
    """
    Handle profile view request from inline button.

    Args:
        callback (CallbackQuery): Telegram callback query.
        session (AsyncSession): SQLAlchemy database session.

    Returns:
        None
    """
    try:
        await cmd_edit_profile(callback, session)
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_view_profile: {e}")
        await callback.message.answer(
            "Произошла ошибка при просмотре анкеты. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

# --------------------------------------------------------------------------------

@router.message(Command("cancel_coffee"))
async def cmd_cancel_coffee(message: Message, session: AsyncSession):
    """
    Cancel user participation in current week's Random Coffee.

    Args:
        message (Message): Telegram command message.
        session (AsyncSession): SQLAlchemy database session.

    Returns:
        None
    """
    try:
        profile = await get_user_profile(session, message.from_user.id)
        if not profile:
            await message.answer(
                "У вас еще нет анкеты Random Coffee. "
                "Используйте /random_coffee для создания анкеты."
            )
            return

        week_start = get_week_start_date()
        participation = await session.scalar(
            select(RandomCoffeeWeek).where(
                RandomCoffeeWeek.user_id == message.from_user.id,
                RandomCoffeeWeek.week_start == week_start.isoformat()
            )
        )

        if not participation or not participation.is_participating:
            await message.answer(
                "Вы не участвуете в Random Coffee на этой неделе."
            )
            return

        pair = await session.scalar(
            select(RandomCoffeePair).where(
                RandomCoffeePair.week_start == week_start.isoformat(),
                (RandomCoffeePair.user1_id == message.from_user.id) |
                (RandomCoffeePair.user2_id == message.from_user.id)
            )
        )

        if pair:
            await message.answer(
                "К сожалению, пары уже созданы, и отменить участие нельзя. "
                "Пожалуйста, свяжитесь с вашим собеседником и договоритесь о встрече."
            )
            return

        participation.is_participating = False
        participation.created_at = datetime.now().isoformat()
        await session.commit()

        await message.answer(
            "Вы успешно отменили участие в Random Coffee на этой неделе. "
            "Надеемся увидеть вас в следующий раз!"
        )
    except Exception as e:
        logger.error(f"Error in cmd_cancel_coffee: {e}")
        await message.answer(
            "Произошла ошибка при отмене участия. "
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )

# --------------------------------------------------------------------------------

@router.message(F.poll_answer)
async def handle_poll_answer(poll_answer: Message, session: AsyncSession):
    """
    Handle poll answer from group chat participants.

    Args:
        poll_answer (Message): Telegram poll answer message.
        session (AsyncSession): SQLAlchemy database session.

    Returns:
        None
    """
    try:
        is_participating = poll_answer.option_ids[0] == 0

        week_start = get_week_start_date()
        existing_participation = await session.scalar(
            select(RandomCoffeeWeek).where(
                RandomCoffeeWeek.user_id == poll_answer.user.id,
                RandomCoffeeWeek.week_start == week_start.isoformat()
            )
        )

        if existing_participation:
            existing_participation.is_participating = is_participating
            existing_participation.created_at = datetime.now().isoformat()
        else:
            participation = RandomCoffeeWeek(
                user_id=poll_answer.user.id,
                week_start=week_start.isoformat(),
                is_participating=is_participating,
                created_at=datetime.now().isoformat()
            )
            session.add(participation)

        await session.commit()
    except Exception as e:
        logger.error(f"Error in handle_poll_answer: {e}")
