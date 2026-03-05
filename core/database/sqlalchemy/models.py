import datetime as dt

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Result,
    SmallInteger,
    delete,
    select,
)
from sqlalchemy.ext.asyncio.session import AsyncSession
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
    datetime: Mapped[dt.datetime] = mapped_column(DateTime)

    @classmethod
    async def get_events_by_user_id(
        cls: type[Event], user_id: int, session: AsyncSession | None = None
    ) -> list[Event]:
        own_session = session is None
        session = session or cls.session_maker()

        try:
            statement = (
                select(cls)
                .join(UserEvent, UserEvent.event_id == cls.id)
                .where(UserEvent.user_id == user_id)
            )
            result: Result[tuple[Event]] = await session.execute(statement=statement)
            return list(result.scalars().all())

        finally:
            if own_session:
                await session.close()


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

    @classmethod
    async def clear_table(cls: type[Link]):
        stmt = delete(cls)
        async with cls.session_maker() as session:
            await session.execute(stmt)
            await session.commit()

    @classmethod
    async def get_first_priority_unverified(
        cls: type[Link], session: AsyncSession | None = None
    ) -> Link | None:
        own_session = session is None
        session = session or cls.session_maker()

        try:
            statement = (
                select(cls)
                .where(Link.is_prohibited.is_(None))
                .order_by(Link.priority.desc())
                .limit(1)
            )
            result: Result[tuple[Link]] = await session.execute(statement=statement)
            return result.scalar_one_or_none()

        finally:
            if own_session:
                await session.close()

    @classmethod
    async def get_by_link(
        cls: type[Link],
        link: str,
        session: AsyncSession | None = None,
    ) -> Link | None:
        result: Link | None = await cls.get_one(session=session, link=link)
        return result
