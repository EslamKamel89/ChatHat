import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import URL, Connection, make_url
from sqlalchemy.ext.asyncio import async_engine_from_config

from chathat.core.database import metadata
from chathat.core.settings.config import Config as AppConfig

config = context.config

if config.config_file_name is not None:
    fileConfig(
        config.config_file_name,
        disable_existing_loggers=False,
    )

target_metadata = metadata


def get_database_url() -> URL:
    configured_url = config.attributes.get("database_url")

    if configured_url is None:
        settings = AppConfig()  # type: ignore
        if settings.database_url is None:
            raise RuntimeError("Migrations require CHATHAT_DATABASE_URL")
        configured_url = settings.database_url.get_secret_value()

    url = make_url(configured_url)

    if url.drivername != "postgresql+asyncpg" or not url.host or not url.database:
        raise RuntimeError("Migrations require a PostgreSQL asyncpg URL")

    return url


def run_migrations_offline() -> None:
    context.configure(
        url=get_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        url=get_database_url(),
        poolclass=pool.NullPool,
        connect_args={"timeout": 5},
        hide_parameters=True,
    )

    try:
        async with connectable.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await connectable.dispose()


def run_migrations_online() -> None:
    supplied_connection = config.attributes.get("connection")

    if supplied_connection is not None:
        do_run_migrations(supplied_connection)
    else:
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
