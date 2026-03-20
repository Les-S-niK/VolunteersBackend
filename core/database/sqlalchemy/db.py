import datetime
from abc import ABC, abstractmethod
from typing import Any, Optional, Type, override

from sqlalchemy import (
    BigInteger,
    DateTime,
    Delete,
    Result,
    Select,
    Update,
    delete,
    func,
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import DBSettings, get_db_settings
from core.logger import database_query_logger, execute_query_logger

settings: DBSettings = get_db_settings()
engine: AsyncEngine = create_async_engine(url=settings.get_db_url())


class QueryAction(ABC):
    @abstractmethod
    async def execute(self) -> Any: ...


class QueryBuilder:
    def __init__(self, stmt: Any) -> None:
        self.stmt = stmt

    def __getattr__(self, item):
        attr = getattr(self.stmt, item)

        if not callable(attr):
            return attr

        def wrapper(*args, **kwargs):
            new_stmt = attr(*args, **kwargs)

            if isinstance(new_stmt, self.stmt.__class__):
                self.stmt = new_stmt
                return self
            return new_stmt

        return wrapper


class AddAction(QueryAction):
    def __init__(self, item: "Base", session: AsyncSession, own_session: bool) -> None:
        self.own_session = own_session
        self.session = session
        self.item = item

    @override
    @execute_query_logger
    async def execute(self) -> None:
        try:
            self.session.add(self.item)
            if self.own_session:
                await self.session.commit()

        except Exception as e:
            if self.own_session:
                await self.session.rollback()

            raise e

        finally:
            if self.own_session:
                await self.session.close()


class GetAction(QueryAction, QueryBuilder):
    def __init__(
        self, model: Type[Base], session: AsyncSession, own_session: bool
    ) -> None:
        self.own_session = own_session
        self.model = model
        self.session = session
        self.stmt: Select = select(model)

    @override
    @execute_query_logger
    async def execute(self) -> Result:
        try:
            result = await self.session.execute(self.stmt)
            return result

        finally:
            if self.own_session:
                await self.session.close()


class UpdateAction(QueryAction, QueryBuilder):
    def __init__(
        self, model: Type[Base], session: AsyncSession, own_session: bool
    ) -> None:
        self.own_session = own_session
        self.model = model
        self.session = session
        self.stmt: Update = update(model)

    @override
    @execute_query_logger
    async def execute(self) -> Result:
        try:
            result = await self.session.execute(self.stmt)
            if self.own_session:
                await self.session.commit()
            return result

        except Exception as e:
            if self.own_session:
                await self.session.rollback()

            raise e

        finally:
            if self.own_session:
                await self.session.close()


class DeleteAction(QueryAction, QueryBuilder):
    def __init__(self, model: Type[Base], session: AsyncSession, own_session: bool):
        self.own_session = own_session
        self.model = model
        self.session = session
        self.stmt: Delete = delete(model)

    @override
    @execute_query_logger
    async def execute(self) -> Result:
        try:
            result = await self.session.execute(self.stmt)
            if self.own_session:
                await self.session.commit()
            return result

        except Exception as e:
            if self.own_session:
                await self.session.rollback()

            raise e

        finally:
            if self.own_session:
                await self.session.close()


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
    @database_query_logger
    def add(
        cls: Type[CRUD], item: "Base", session: Optional[AsyncSession] = None
    ) -> AddAction:
        return AddAction(
            item=item,
            session=session or cls.__async_session_maker(),
            own_session=session is None,
        )

    @classmethod
    @database_query_logger
    def get(
        cls: Type[CRUD], model: Type[Base], session: Optional[AsyncSession] = None
    ) -> GetAction:
        return GetAction(
            model=model,
            session=session or cls.__async_session_maker(),
            own_session=session is None,
        )

    @classmethod
    @database_query_logger
    def update(
        cls: Type[CRUD], model: Type[Base], session: Optional[AsyncSession] = None
    ) -> UpdateAction:
        return UpdateAction(
            model=model,
            session=session or cls.__async_session_maker(),
            own_session=session is None,
        )

    @classmethod
    @database_query_logger
    def delete(
        cls: Type[CRUD], model: Type[Base], session: Optional[AsyncSession] = None
    ) -> DeleteAction:
        return DeleteAction(
            model=model,
            session=session or cls.__async_session_maker(),
            own_session=session is None,
        )

    async def __aenter__(self):
        self.__local_session = self.__async_session_maker()
        return self.__local_session

    async def __aexit__(self, *_):
        await self.__local_session.commit()
        await self.__local_session.close()
        return False


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


async def drop_db():
    try:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.drop_all)
    except Exception as a:
        print(a)
