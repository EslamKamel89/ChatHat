from dataclasses import dataclass

from pydantic import SecretStr
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine
from sqlmodel.ext.asyncio.session import AsyncSession


@dataclass(frozen=True, slots=True)
class Database:
    engine: AsyncEngine
    sessions: async_sessionmaker[AsyncSession]


def create_database(url: SecretStr) -> Database:
    engine = create_async_engine(
        url.get_secret_value(),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=10,
        connect_args={"timeout": 5},
        hide_parameters=True,
    )
    return Database(
        engine=engine,
        sessions=async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        ),
    )
