import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    ForeignKey,
    Select,
    SmallInteger,
    delete,
    select,
)
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Mapped, MappedColumn, mapped_column

from core.database.sqlalchemy.db import Base


class User(Base):
    __tablename__ = "users"

    full_name: Mapped[str]
    birth: Mapped[datetime.date] = mapped_column(Date)
    passport: Mapped[str]
    phone_number: Mapped[str]
    points: Mapped[int] = mapped_column(default="0", server_default="0")
    password: Mapped[str]
    telegram_id: Mapped[int | None] = mapped_column(BigInteger)
    city_id: Mapped[int] = mapped_column(SmallInteger)


class Event(Base):
    __tablename__ = "events"

    name: Mapped[str]
    date: Mapped[datetime.date] = mapped_column(Date)


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
    async def get_first_unverified(
        cls: type[Link], session: AsyncSession | None = None
    ) -> Link | None:
        own_session: bool = session is None
        session = session or cls.session_maker()

        try:
            stmt: Select[tuple[Link]] = select(cls).where(cls.is_prohibited.is_(None))
            result = await session.execute(stmt)
            return result.scalars().first()

        except SQLAlchemyError as e:
            print(e)
            return None

        finally:
            if own_session:
                await session.close()
