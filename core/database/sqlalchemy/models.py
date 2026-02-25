import datetime

from sqlalchemy import BigInteger, Date, ForeignKey, SmallInteger
from sqlalchemy.orm import Mapped, mapped_column

from core.database.sqlalchemy.db import Base


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str]
    birth: Mapped[datetime.date] = mapped_column(Date)
    city_id: Mapped[int] = mapped_column(SmallInteger)
    passport: Mapped[str]
    phone_number: Mapped[str]
    points: Mapped[int] = mapped_column(default="0", server_default="0")
    password: Mapped[str]
    telegram_id: Mapped[int | None] = mapped_column(BigInteger)


class Event(Base):
    __tablename__ = "events"

    event_name: Mapped[str]
    date: Mapped[datetime.date] = mapped_column(Date)


class UserEvent(Base):
    __tablename__ = "users_events"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("events.id"))


class Link(Base):
    __tablename__ = "links"

    link: Mapped[str] = mapped_column(unique=True)
    is_checked: Mapped[bool]
    is_cool: Mapped[bool]
