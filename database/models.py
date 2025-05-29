"""
Database Models
SQLAlchemy models for users, club_events, vacancies, and registrations.
"""

# --------------------------------------------------------------------------------

from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, BigInteger, ForeignKey
from sqlalchemy import String
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column

from config.settings import SQL_URL

# --------------------------------------------------------------------------------

engine = create_async_engine(url=SQL_URL, echo=True)
async_session = async_sessionmaker(engine)


# --------------------------------------------------------------------------------


class Base(AsyncAttrs, DeclarativeBase):
    """Base class for SQLAlchemy models."""
    pass


# --------------------------------------------------------------------------------


class User(Base):
    """User model representing a bot user.

    Args:
        id (BigInteger): Primary key.
        handler (str): User's handler.
        is_superuser (bool): Indicates superuser status.
        event_cnt (int): Number of club_events the user has.
        strick (int): User's streak.
        first_contact (str): First contact value.
        money (int): Amount of money.
        ref_cnt (int): Referral count.

    Returns:
        User: SQLAlchemy user model instance.
    """
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True)
    handler = Column(String, nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    event_cnt = Column(Integer, nullable=False, default=0)
    strick = Column(Integer, nullable=False, default=0)
    first_contact = Column(String, default='')
    money = Column(Integer, nullable=False, default=1)
    ref_cnt = Column(Integer, nullable=False, default=0)


# --------------------------------------------------------------------------------


class Questionary(Base):
    """Questionary model storing user's application info.

    Args:
        user_id (BigInteger): Foreign key to user.
        full_name (str): Full name.
        degree (str): Academic degree.
        course (str): Study course.
        program (str): Study program.
        email (str): Email address.
        vacancy (str): Vacancy applied for.
        motivation (str): Motivation text.
        plans (str): Future plans.
        strengths (str): User strengths.
        career_goals (str): Career goals.
        team_motivation (str): Team motivation.
        role_in_team (str): Role in a team.
        events (str): Events attended.
        found_info (str): How user found out.
        resume (str): Resume link or text.

    Returns:
        Questionary: SQLAlchemy questionary model instance.
    """
    __tablename__ = "questionary"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    full_name = Column(String, default='')
    degree = Column(String, default='')
    course = Column(String, default='')
    program = Column(String, default='')
    email = Column(String, default='')
    vacancy = Column(String, default='')
    motivation = Column(String, default='')
    plans = Column(String, default='')
    strengths = Column(String, default='')
    career_goals = Column(String, default='')
    team_motivation = Column(String, default='')
    role_in_team = Column(String, default='')
    events = Column(String, default='')
    found_info = Column(String, default='')
    resume = Column(String, default='')


# --------------------------------------------------------------------------------


class Event(Base):
    """Event model representing a bot event.

    Args:
        name (str): Event name.
        desc (str): Event description.
        date (str): Event date.
        status (str): Event status.
        time (str): Event time.
        place (str): Event location.
        winner (BigInteger): Winner user ID.

    Returns:
        Event: SQLAlchemy event model instance.
    """
    __tablename__ = "event"

    name = Column(String, primary_key=True)
    desc = Column(String)
    date = Column(String)
    status = Column(String)
    time = Column(String, default='')
    place = Column(String, default='')
    winner = Column(BigInteger)


# --------------------------------------------------------------------------------


class UserXEvent(Base):
    """UserXEvent model representing user registration to an event.

    Args:
        user_id (BigInteger): Foreign key to user.
        event_name (str): Foreign key to event.
        status (str): Registration status.
        first_contact (str): First contact value.

    Returns:
        UserXEvent: SQLAlchemy user-event relation model.
    """
    __tablename__ = "user_x_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    status = Column(String, default='')
    first_contact = Column(String, default='')


# --------------------------------------------------------------------------------


class Vacancy(Base):
    """Vacancy model representing available positions.

    Args:
        name (str): Name of the vacancy.

    Returns:
        Vacancy: SQLAlchemy vacancy model instance.
    """
    __tablename__ = "vacancy"

    name = Column(String, primary_key=True)


# --------------------------------------------------------------------------------


class RegEvent(Base):
    """RegEvent model for generic event registrations.

    Args:
        id (BigInteger): Primary key.
        name (str): First name.
        surname (str): Surname.
        fathername (str): Middle name.
        mail (str): Email address.
        phone (str): Phone number.
        org (str): Organization name.

    Returns:
        RegEvent: SQLAlchemy registration model instance.
    """
    __tablename__ = "reg_event"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, default='')
    surname = Column(String, default='')
    fathername = Column(String, default='')
    mail = Column(String, default='')
    phone = Column(String, default='')
    org = Column(String, default='')


# --------------------------------------------------------------------------------


class RefGiveAway(Base):
    """RefGiveAway model for referrals in giveaways.

    Args:
        user_id (BigInteger): User ID.
        event_name (str): Event name.
        host_id (BigInteger): Host user ID.

    Returns:
        RefGiveAway: SQLAlchemy referral model instance.
    """
    __tablename__ = "reg_give_away"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    host_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)


# --------------------------------------------------------------------------------


class GiveAwayHost(Base):
    """GiveAwayHost model representing event hosts.

    Args:
        user_id (BigInteger): Host user ID.
        event_name (str): Event name.
        org_name (str): Organization name.

    Returns:
        GiveAwayHost: SQLAlchemy host model instance.
    """
    __tablename__ = "give_away_host"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    org_name = Column(String, default='')


# --------------------------------------------------------------------------------


class Networking(Base):
    """Networking model placeholder.

    Args:
        id (BigInteger): Primary key.

    Returns:
        Networking: SQLAlchemy networking model instance.
    """
    __tablename__ = "networking"

    id = Column(BigInteger, primary_key=True, autoincrement=True)


# --------------------------------------------------------------------------------


class EventAttendance(Base):
    """EventAttendance model for tracking user attendance at club_events.

    Args:
        id (Integer): Primary key.
        user_id (BigInteger): Foreign key to user.
        event_name (String): Foreign key to event.
        attended_at (String): Timestamp of attendance.
        verified_by (BigInteger): Foreign key to user (superuser who verified).

    Returns:
        EventAttendance: SQLAlchemy attendance model instance.
    """
    __tablename__ = "event_attendance"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    attended_at = Column(String, nullable=False)  # Store as ISO format string
    verified_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)


# --------------------------------------------------------------------------------


class QRCode(Base):
    """QRCode model for storing QR code data.

    Args:
        id (Integer): Primary key.
        user_id (BigInteger): Foreign key to user.
        event_name (String): Foreign key to event.
        created_at (String): Timestamp of creation.
        is_used (Boolean): Whether the QR code has been used.

    Returns:
        QRCode: SQLAlchemy QR code model instance.
    """
    __tablename__ = "qr_code"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    created_at = Column(String, nullable=False)  # Store as ISO format string
    is_used = Column(Boolean, nullable=False, default=False)


# --------------------------------------------------------------------------------


class FaceControl(Base):
    """FaceControl model for storing face control users who can verify QR codes.

    Args:
        id (Integer): Primary key.
        user_id (BigInteger): Foreign key to user who has face control permissions.
        added_by (BigInteger): Foreign key to user (admin) who granted the permission.
        added_at (String): Timestamp when permission was granted.
        username (String): Telegram username of the face control user.
        full_name (String): Full name of the face control user.

    Returns:
        FaceControl: SQLAlchemy face control model instance.
    """
    __tablename__ = "face_control"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, unique=True)
    added_by = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    added_at = Column(String, nullable=False)  # Store as ISO format string
    username = Column(String, nullable=True)  # Telegram username
    full_name = Column(String, nullable=True)  # Full name from Telegram


# --------------------------------------------------------------------------------


class RandomCoffeeProfile(Base):
    """RandomCoffeeProfile model for storing user profiles for Random Coffee.

    Args:
        id (Integer): Primary key.
        user_id (BigInteger): Foreign key to user.
        full_name (String): User's full name.
        city (String): User's city.
        social_links (String): User's social media links.
        occupation (String): What user does.
        hobbies (String): User's hobbies.
        birth_date (String): User's birth date in DD.MM.YYYY format.
        meeting_goal (String): User's goal for meetings (fun/benefit ratio).
        meeting_format (String): Preferred meeting format (online/offline).
        created_at (String): Timestamp when profile was created.
        updated_at (String): Timestamp when profile was last updated.

    Returns:
        RandomCoffeeProfile: SQLAlchemy random coffee profile model instance.
    """
    __tablename__ = "random_coffee_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False, unique=True)
    full_name = Column(String, nullable=False)
    city = Column(String, nullable=False)
    social_links = Column(String, nullable=False)
    occupation = Column(String, nullable=False)
    hobbies = Column(String, nullable=False)
    birth_date = Column(String, nullable=False)
    meeting_goal = Column(String, nullable=False)
    meeting_format = Column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )


class RandomCoffeeWeek(Base):
    """RandomCoffeeWeek model for tracking weekly participation.

    Args:
        id (Integer): Primary key.
        user_id (BigInteger): Foreign key to user.
        week_start (String): Start date of the week in ISO format.
        is_participating (Boolean): Whether user is participating this week.
        created_at (String): Timestamp when participation was recorded.

    Returns:
        RandomCoffeeWeek: SQLAlchemy random coffee week model instance.
    """
    __tablename__ = "random_coffee_weeks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    week_start = Column(String, nullable=False)  # Store as ISO format string
    is_participating = Column(Boolean, nullable=False, default=True)
    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )


class RandomCoffeePair(Base):
    """RandomCoffeePair model for storing weekly pairs.

    Args:
        id (Integer): Primary key.
        week_start (String): Start date of the week in ISO format.
        user1_id (BigInteger): First user's ID.
        user2_id (BigInteger): Second user's ID.
        created_at (String): Timestamp when pair was created.

    Returns:
        RandomCoffeePair: SQLAlchemy random coffee pair model instance.
    """
    __tablename__ = "random_coffee_pairs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    week_start = Column(String, nullable=False)  # Store as ISO format string
    user1_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    user2_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )


class RandomCoffeeFeedback(Base):
    """RandomCoffeeFeedback model for storing meeting feedback.

    Args:
        id (Integer): Primary key.
        pair_id (Integer): Foreign key to random coffee pair.
        user_id (BigInteger): Foreign key to user giving feedback.
        rating (Integer): Rating from 1 to 5.
        comment (String): Optional feedback comment.
        created_at (String): Timestamp when feedback was given.

    Returns:
        RandomCoffeeFeedback: SQLAlchemy random coffee feedback model instance.
    """
    __tablename__ = "random_coffee_feedback"

    id = Column(Integer, primary_key=True, autoincrement=True)
    pair_id = Column(Integer, ForeignKey("random_coffee_pairs.id"), nullable=False)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )


class RandomCoffeeGroupSettings(Base):
    """RandomCoffeeGroupSettings model for storing group chat settings.

    Args:
        id (Integer): Primary key.
        chat_id (BigInteger): Telegram chat ID.
        reminder_day (String): Day of week for reminders (e.g., "Friday").
        reminder_time (String): Time for reminders (e.g., "10:00").
        pairing_day (String): Day of week for pairing (e.g., "Monday").
        pairing_time (String): Time for pairing (e.g., "10:00").
        created_at (String): Timestamp when settings were created.
        updated_at (String): Timestamp when settings were last updated.

    Returns:
        RandomCoffeeGroupSettings: SQLAlchemy random coffee group settings model instance.
    """
    __tablename__ = "random_coffee_group_settings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, unique=True)
    reminder_day = Column(String, nullable=False)
    reminder_time = Column(String, nullable=False)
    pairing_day = Column(String, nullable=False)
    pairing_time = Column(String, nullable=False)
    created_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat()
    )
    updated_at: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=lambda: datetime.utcnow().isoformat(),
        onupdate=lambda: datetime.utcnow().isoformat()
    )


# --------------------------------------------------------------------------------


async def async_main():
    """Initialize database schema.

    Connects to the database and creates all tables.

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
