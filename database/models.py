"""
Database Models
SQLAlchemy models for users, events, vacancies, and registrations.
"""

# --------------------------------------------------------------------------------

from sqlalchemy import Column, Integer, String, Boolean, BigInteger, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

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
        event_cnt (int): Number of events the user has.
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
    """EventAttendance model for tracking user attendance at events.

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


async def async_main():
    """Initialize database schema.

    Connects to the database and creates all tables.

    Returns:
        None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
