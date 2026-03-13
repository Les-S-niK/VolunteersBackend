import datetime as dt
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    DECIMAL,
    TEXT,
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    SmallInteger,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from core.database.sqlalchemy.db import Base


class PurchaseStatuses(str, Enum):
    frozen = "frozen"
    denied = "denied"
    purchased = "purchased"


class ReportStatuses(str, Enum):
    answered = "answered"
    unanswered = "unanswered"


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
    priority: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        default=None,
        doc="Link priority from 0.0 to 10.0 where 10 - the most important. None - priority not entered.",
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True,
        default=None,
        doc="The user who should check this link. None - no one took this link to check it.",
    )


class Report(Base):
    __tablename__ = "reports"

    title: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(TEXT)
    status: Mapped[ReportStatuses] = mapped_column(default=ReportStatuses.unanswered)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), doc="The user who create a report."
    )


class Good(Base):
    __tablename__ = "goods"

    image_url: Mapped[str] = mapped_column(String)
    price: Mapped[Decimal] = mapped_column(DECIMAL)
    amount: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String)


class UserGood(Base):
    __tablename__ = "users_goods"

    status: Mapped[PurchaseStatuses] = mapped_column(default=PurchaseStatuses.frozen)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.id"), doc="The user who bought the good."
    )
    good_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("goods.id"), doc="The good that bought by the user."
    )
