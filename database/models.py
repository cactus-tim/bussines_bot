from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, ARRAY, BigInteger, ForeignKey, Numeric, JSON, Date
from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
from bot_instance import SQL_URL_RC

engine = create_async_engine(url=SQL_URL_RC, echo=True)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id = Column(BigInteger, primary_key=True, index=True)
    handler = Column(String, nullable=False)
    is_superuser = Column(Boolean, nullable=False, default=False)
    event_cnt = Column(Integer, nullable=False, default=0)
    strick = Column(Integer, nullable=False, default=0)
    first_contact = Column(String, default='')
    money = Column(Integer, nullable=False, default=1)
    ref_cnt = Column(Integer, nullable=False, default=0)


class Questionary(Base):
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


class Event(Base):
    __tablename__ = "event"

    name = Column(String, primary_key=True)
    desc = Column(String)
    date = Column(String)
    status = Column(String)  # in_progress end
    time = Column(String, default='')
    place = Column(String, default='')
    winner = Column(BigInteger)


class UserXEvent(Base):
    __tablename__ = "user_x_event"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    status = Column(String, default='')  # reg, been, nbeeb (after event all reg -> nbeen)
    first_contact = Column(String, default='')


class Vacancy(Base):
    __tablename__ = "vacancy"

    name = Column(String, primary_key=True)


class RegEvent(Base):
    __tablename__ = "reg_event"

    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, default='')
    surname = Column(String, default='')
    fathername = Column(String, default='')
    mail = Column(String, default='')
    phone = Column(String, default='')
    org = Column(String, default='')


class RefGiveAway(Base):
    __tablename__ = "reg_give_away"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    host_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)


class GiveAwayHost(Base):
    __tablename__ = "give_away_host"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey("user.id"), nullable=False)
    event_name = Column(String, ForeignKey("event.name"), nullable=False)
    org_name = Column(String, default='')


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
