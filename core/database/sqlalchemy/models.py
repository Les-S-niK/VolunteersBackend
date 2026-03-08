import datetime as dt

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    SmallInteger,
)
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from core.database.sqlalchemy.db import Base


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str]
    birth: Mapped[dt.date] = mapped_column(Date)
    passport: Mapped[str]
    phone_number: Mapped[str]
    points: Mapped[int] = mapped_column(default="0", server_default="0")
    password: Mapped[str]
    telegram_id: Mapped[int | None] = mapped_column(BigInteger)
    city_id: Mapped[int] = mapped_column(SmallInteger)


class Event(Base):
    __tablename__ = "events"

    name: Mapped[str]
    datetime: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True))


class UserEvent(Base):
    __tablename__ = "users_events"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    event_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("events.id"))


class Link(Base):
    __tablename__ = "links"

    link: Mapped[str] = mapped_column(unique=True)
    is_prohibited: Mapped[bool | None] = mapped_column(
        Boolean,
        nullable=True,
        default=None,
        doc="Is link prohibited? True - yes, False - no. None - not checked.",
    )
    priority: MappedColumn[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
        doc="Link priority from 0.0 to 10.0 where 10 - the most important. None - priority not entered.",
    )
    user_id: MappedColumn[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
        default=None,
        doc="The user who should check this link. None - no one took this link to check it.",
    )
