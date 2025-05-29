"""
Random Coffee Scheduler

Scheduler service for sending reminders and pairing participants.
"""

# --------------------------------------------------------------------------------

from datetime import datetime
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy import select

from config.settings import GLOBAL_REMINDER, GLOBAL_PAIRING
from database.models import RandomCoffeeGroupSettings, RandomCoffeeProfile, RandomCoffeeWeek
from database.req.random_coffee import get_participating_users, save_pairs, get_user_profile
from keyboards.random_coffee.base import get_weekly_participation_keyboard, user_send_message_kb
from .helpers import (
    get_week_start_date,
    create_smart_pairs,
    format_pairs_message,
    get_profile_text,
    get_day
)

# --------------------------------------------------------------------------------

class RandomCoffeeScheduler:
    """
    Scheduler for Random Coffee functionality.

    Schedules reminders and pairing jobs globally or per group chat.
    """

    def __init__(self, bot, session_maker):
        """
        Initialize scheduler.

        Args:
            bot: Telegram bot instance.
            session_maker: SQLAlchemy async session maker.
        """
        self.bot = bot
        self.session_maker = session_maker
        self.scheduler = AsyncIOScheduler()

    # --------------------------------------------------------------------------------

    async def send_reminder(self, chat_id: int, is_group: bool = False):
        """
        Send participation reminder to a group or private chat.

        Args:
            chat_id (int): Telegram chat ID.
            is_group (bool): Whether chat is a group.

        Returns:
            None
        """
        if is_group:
            await self.bot.send_poll(
                chat_id=chat_id,
                question="Участвуешь в Random Coffee на следующей неделе?",
                options=["Да", "Нет"],
                is_anonymous=False
            )
        else:
            await self.bot.send_message(
                chat_id=chat_id,
                text="Вы хотите участвовать в Random Coffee на следующей неделе?",
                reply_markup=get_weekly_participation_keyboard()
            )

    # --------------------------------------------------------------------------------

    async def create_pairs(self, chat_id: int, chat_title: Optional[str] = None):
        """
        Create and send pairs for the week to a group chat.

        Args:
            chat_id (int): Telegram chat ID.
            chat_title (Optional[str]): Title of the chat.

        Returns:
            None
        """
        async with self.session_maker() as session:
            week_start = get_week_start_date()
            users = await get_participating_users(session, week_start)

            if len(users) < 2:
                await self.bot.send_message(
                    chat_id=chat_id,
                    text="Недостаточно участников для создания пар на этой неделе 😔"
                )
                return

            pairs = await create_smart_pairs(session, users)
            await save_pairs(session, pairs, week_start)

            message = format_pairs_message(pairs, chat_title or "Random Coffee")
            await self.bot.send_message(chat_id=chat_id, text=message)

    # --------------------------------------------------------------------------------

    async def setup_group_schedule(
        self,
        chat_id: int,
        reminder_day: str,
        reminder_time: str,
        pairing_day: str,
        pairing_time: str
    ):
        """
        Set up scheduled reminder and pairing jobs for a group chat.

        Args:
            chat_id (int): Group chat ID.
            reminder_day (str): Day of week for reminder.
            reminder_time (str): Time (HH:MM) for reminder.
            pairing_day (str): Day of week for pairing.
            pairing_time (str): Time (HH:MM) for pairing.

        Returns:
            None
        """
        async with self.session_maker() as session:
            settings = RandomCoffeeGroupSettings(
                chat_id=chat_id,
                reminder_day=reminder_day,
                reminder_time=reminder_time,
                pairing_day=pairing_day,
                pairing_time=pairing_time,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            session.add(settings)
            await session.commit()

        reminder_trigger = CronTrigger(
            day_of_week=reminder_day.lower(),
            hour=reminder_time.split(":")[0],
            minute=reminder_time.split(":")[1]
        )

        pairing_trigger = CronTrigger(
            day_of_week=pairing_day.lower(),
            hour=pairing_time.split(":")[0],
            minute=pairing_time.split(":")[1]
        )

        self.scheduler.add_job(
            self.send_reminder,
            trigger=reminder_trigger,
            args=[chat_id, True],
            id=f"reminder_{chat_id}"
        )

        self.scheduler.add_job(
            self.create_pairs,
            trigger=pairing_trigger,
            args=[chat_id],
            id=f"pairing_{chat_id}"
        )

    # --------------------------------------------------------------------------------

    async def send_reminders_to_all_users(self):
        """
        Send weekly reminder to all users with existing profiles.

        Returns:
            None
        """
        async with self.session_maker() as session:
            week_start = get_week_start_date()
            profiles = await session.execute(select(RandomCoffeeProfile))
            profiles = profiles.scalars().all()

            for profile in profiles:
                participation = await session.scalar(
                    select(RandomCoffeeWeek).where(
                        RandomCoffeeWeek.user_id == profile.user_id,
                        RandomCoffeeWeek.week_start == week_start.isoformat()
                    )
                )
                if participation and participation.is_participating:
                    continue

                try:
                    await self.bot.send_message(
                        chat_id=profile.user_id,
                        text="Вы хотите участвовать в Random Coffee на следующей неделе?",
                        reply_markup=get_weekly_participation_keyboard()
                    )
                except Exception as e:
                    print(f"Ошибка при отправке напоминания {profile.user_id}: {e}")

    # --------------------------------------------------------------------------------

    async def create_global_pairs(self):
        """
        Create and send private pair messages to all participating users.

        Returns:
            None
        """
        async with self.session_maker() as session:
            week_start = get_week_start_date()
            users = await get_participating_users(session, week_start)

            if len(users) < 2:
                print("Недостаточно участников для глобального распределения")
                return

            pairs = await create_smart_pairs(session, users)
            await save_pairs(session, pairs, week_start)

            for user1, user2 in pairs:
                profile1 = await get_user_profile(session, user1.id)
                profile2 = await get_user_profile(session, user2.id)

                try:
                    await self.bot.send_message(
                        chat_id=user1.id,
                        text=f"Привет!👋 \n"
                             f"Твоя пара на эту неделю:\n\n"
                             f"{get_profile_text(profile2)}\n\n"
                             f"Напиши собеседнику сразу, чтобы не забыть.\n"
                             f"Будут вопросы, пиши в ответ!",
                        reply_markup=user_send_message_kb(user2.id)
                    )
                    await self.bot.send_message(
                        chat_id=user2.id,
                        text=f"Привет!👋 \n"
                             f"Твоя пара на эту неделю:\n\n"
                             f"{get_profile_text(profile1)}\n\n"
                             f"Напиши собеседнику сразу, чтобы не забыть.\n"
                             f"Будут вопросы, пиши в ответ!",
                        reply_markup=user_send_message_kb(user1.id)
                    )
                except Exception as e:
                    print(f"Ошибка при отправке сообщения паре: {e}")

    # --------------------------------------------------------------------------------

    def start(self):
        """
        Start the scheduler and add global jobs.

        Returns:
            None
        """
        self.scheduler.start()

        self.scheduler.add_job(
            self.send_reminders_to_all_users,
            trigger=CronTrigger(
                day_of_week=get_day(GLOBAL_REMINDER.get("day")),
                hour=GLOBAL_REMINDER.get("hour"),
                minute=GLOBAL_REMINDER.get("minute")
            ),
            id="global_reminder"
        )

        self.scheduler.add_job(
            self.create_global_pairs,
            trigger=CronTrigger(
                day_of_week=get_day(GLOBAL_PAIRING.get("day")),
                hour=GLOBAL_PAIRING.get("hour"),
                minute=GLOBAL_PAIRING.get("minute")
            ),
            id="global_pairing"
        )

    # --------------------------------------------------------------------------------

    def shutdown(self):
        """
        Shutdown the scheduler.

        Returns:
            None
        """
        self.scheduler.shutdown()
