import datetime
from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import BigInteger, DateTime, Select, delete, func, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import DBSettings, get_db_settings

settings: DBSettings = get_db_settings()
T = TypeVar("T", bound="Base")

engine: AsyncEngine = create_async_engine(url=settings.get_db_url())  # echo=True
# async_session_maker: AsyncSession = async_sessionmaker(engine, expire_on_commit=False)


class CRUD:
    __engine = engine
    __async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

    @classmethod
    def engine(cls) -> AsyncEngine:
        return cls.__engine

    @classmethod
    def async_session_maker(cls) -> async_sessionmaker[AsyncSession]:
        return cls.__async_session_maker

    @classmethod
    def _build_conditions(cls, **kwargs) -> list[Any]:
        conditions: list[Any] = []

        for field_name, value in kwargs.items():
            if value is not None:
                conditions.append(getattr(cls, field_name) == value)

        return conditions

    @classmethod
    async def add(
        cls: Type[T], session: Optional[AsyncSession] = None, **kwargs
    ) -> Optional[T]:
        own_session = session is None
        session = session or cls.__async_session_maker()

        try:
            instance = cls(**kwargs)
            session.add(instance)

            if own_session:
                await session.commit()
                await session.refresh(instance)

            return instance

        except SQLAlchemyError as e:
            if own_session:
                await session.rollback()
            print(e)
            return None

        finally:
            if own_session:
                await session.close()

    @classmethod
    async def get(
        cls: Type[T], session: Optional[AsyncSession] = None, **filters
    ) -> Optional[List[T]]:
        own_session = session is None
        session = session or cls.__async_session_maker()

        try:
            conditions = cls._build_conditions(**filters)
            stmt: Select = select(cls).where(*conditions)

            result = await session.execute(stmt)
            return result.scalars().all()

        except SQLAlchemyError as e:
            print(e)
            return None

        finally:
            if own_session:
                await session.close()

    @classmethod
    async def get_one(
        cls: Type[T], session: Optional[AsyncSession] = None, **filters
    ) -> Optional[T]:
        own_session = session is None
        session = session or cls.__async_session_maker()

        try:
            conditions = cls._build_conditions(**filters)
            stmt = select(cls).where(*conditions)

            result = await session.execute(stmt)
            return result.scalars().first()

        except SQLAlchemyError as e:
            print(e)
            return None

        finally:
            if own_session:
                await session.close()

    @classmethod
    async def get_by_id(
        cls: Type[T], id: int, session: Optional[AsyncSession] = None
    ) -> Optional[T]:
        return await cls.get_one(session=session, id=id)

    @classmethod
    async def get_all(
        cls: Type[T], session: Optional[AsyncSession] = None
    ) -> Optional[List[T]]:
        return await cls.get(session=session)

    @classmethod
    async def update(
        cls: Type[T], id: int, session: Optional[AsyncSession] = None, **values
    ) -> bool:
        own_session = session is None
        session = session or cls.__async_session_maker()

        try:
            stmt = (
                update(cls)
                .where(cls.id == id)
                .values(**values)
                .execution_options(synchronize_session="fetch")
            )

            result = await session.execute(stmt)

            if own_session:
                await session.commit()

            return result.rowcount > 0

        except SQLAlchemyError as e:
            if own_session:
                await session.rollback()
            print(e)
            return False

        finally:
            if own_session:
                await session.close()

    @classmethod
    async def delete(
        cls: Type[T], id: int, session: Optional[AsyncSession] = None
    ) -> bool:
        own_session = session is None
        session = session or cls.__async_session_maker()

        try:
            stmt = delete(cls).where(cls.id == id)
            result = await session.execute(stmt)

            if own_session:
                await session.commit()

            return result.rowcount > 0

        except SQLAlchemyError as e:
            if own_session:
                await session.rollback()
            print(e)
            return False

        finally:
            if own_session:
                await session.close()

    @classmethod
    async def exists(
        cls: Type[T], session: Optional[AsyncSession] = None, **filters
    ) -> bool:
        result = await cls.get_one(session=session, **filters)
        return result is not None

    @classmethod
    async def count(
        cls: Type[T], session: Optional[AsyncSession] = None, **filters
    ) -> int:
        own_session = session is None
        session = session or cls.__async_session_maker()

        try:
            conditions = cls._build_conditions(**filters)
            stmt = select(func.count()).select_from(cls).where(*conditions)

            result = await session.execute(stmt)
            return result.scalar_one()

        except SQLAlchemyError as e:
            print(e)
            return 0

        finally:
            if own_session:
                await session.close()


class Base(AsyncAttrs, DeclarativeBase, CRUD):
    __abstract__ = True

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


async def init_db():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    except Exception as a:
        print(a)
