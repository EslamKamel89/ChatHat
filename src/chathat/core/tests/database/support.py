import asyncio
import re
from collections.abc import AsyncGenerator, AsyncIterator, Iterator
from contextlib import asynccontextmanager, contextmanager
from uuid import uuid4

import asyncpg
from alembic import command
from alembic.config import Config as AlembicConfig
from pydantic import SecretStr
from sqlalchemy.engine import URL

from chathat.core.database.sessions import Database, create_database

ADMIN_URL = URL.create(
    "postgresql+asyncpg",
    username="chathat_test_admin",
    password="public-test-fixture",
    host="test-db",
    port=5432,
    database="postgres",
)

DATABASE_NAME = re.compile(r"chathat_test_[0-9a-f]{32}")


def require_test_url(url: URL) -> None:
    if (
        url.drivername != ADMIN_URL.drivername
        or url.host != ADMIN_URL.host
        or url.port != ADMIN_URL.port
        or url.username != ADMIN_URL.username
        or url.password != ADMIN_URL.password
        or url.query
        or DATABASE_NAME.fullmatch(url.database or "") is None
    ):
        raise ValueError("Refusing a non-isolated test database target")


@asynccontextmanager
async def admin_connection() -> AsyncGenerator[asyncpg.Connection]:
    connection = await asyncpg.connect(
        ADMIN_URL.set(drivername="postgresql").render_as_string(hide_password=False),
        timeout=5,
        command_timeout=10,
    )
    try:
        identity = await connection.fetchrow(
            "SELECT current_database() AS database, current_user AS role"
        )
        if (
            identity["database"] != "postgres"
            or identity["role"] != "chathat_test_admin"
        ):
            raise RuntimeError("Unexpected test administration connection")
        yield connection
    finally:
        await connection.close()


@asynccontextmanager
async def target_connection(url: URL) -> AsyncGenerator[asyncpg.Connection]:
    require_test_url(url)
    connection = await asyncpg.connect(
        url.set(drivername="postgresql").render_as_string(hide_password=False),
        timeout=5,
        command_timeout=10,
    )
    try:
        yield connection
    finally:
        await connection.close()


async def scalar(url: URL, statement: str) -> object:
    async with target_connection(url) as connection:
        return await connection.fetchval(statement)


async def execute(url: URL, statement: str) -> None:
    async with target_connection(url) as connection:
        await connection.execute(statement)


async def postgres_pid1_start(connection: asyncpg.Connection) -> int:
    name = await connection.fetchval("SELECT pg_read_file('/proc/1/comm', 0, 128)")
    if name.strip() != "postgres":
        raise RuntimeError("Refusing restart: PostgreSQL must be container PID 1")

    stat = await connection.fetchval("SELECT pg_read_file('/proc/1/stat', 0, 4096)")
    # Fields after the parenthesized command start at field 3; starttime is 22.
    return int(stat.rsplit(") ", 1)[1].split()[19])


async def restart_test_database(url: URL) -> tuple[int, int]:
    require_test_url(url)

    async with target_connection(url) as connection:
        marker = await connection.fetchval("SHOW cluster_name")
        if marker != "chathat_test_restartable":
            raise RuntimeError(
                "Refusing restart: refresh the normal development stack "
                "to apply the test-db restart configuration"
            )

        before = await postgres_pid1_start(connection)
        started_at = await connection.fetchval("SELECT pg_postmaster_start_time()")
        uptime = await connection.fetchval(
            "SELECT extract(epoch FROM clock_timestamp() - pg_postmaster_start_time())"
        )
        # Docker arms restart monitoring after ten seconds of successful uptime.
        await asyncio.sleep(max(0.0, 11.0 - float(uptime)))

        try:
            # A fixed command on the allowlisted server, never user-supplied SQL.
            # SIGINT requests fast, orderly shutdown of the container's PID 1.
            await connection.execute("COPY (SELECT 1) TO PROGRAM 'kill -INT 1'")
        except (asyncpg.PostgresConnectionError, asyncpg.AdminShutdownError):
            # Shutdown can disconnect this backend before COPY returns.
            pass

    deadline = asyncio.get_running_loop().time() + 45
    last_error: Exception | None = None
    while asyncio.get_running_loop().time() < deadline:
        try:
            async with target_connection(url) as connection:
                after = await postgres_pid1_start(connection)
                restarted_at = await connection.fetchval(
                    "SELECT pg_postmaster_start_time()"
                )
                if after != before and restarted_at > started_at:
                    return before, after
        except (
            OSError,
            asyncpg.PostgresConnectionError,
            asyncpg.CannotConnectNowError,
            asyncpg.AdminShutdownError,
        ) as error:
            last_error = error
        await asyncio.sleep(0.2)

    raise RuntimeError(
        "test-db did not restart and become ready within 45 seconds"
    ) from last_error


async def drop_test_database(url: URL) -> None:
    require_test_url(url)

    async with admin_connection() as connection:
        owner = await connection.fetchval(
            """
            SELECT pg_get_userbyid(datdba)
            FROM pg_database
            WHERE datname = $1
            """,
            url.database,
        )
        if owner != ADMIN_URL.username:
            raise RuntimeError("Refusing cleanup of an unowned database")

        await connection.execute(f'DROP DATABASE "{url.database}" WITH (FORCE)')

        remaining = await connection.fetchval(
            "SELECT count(*) FROM pg_database WHERE datname = $1",
            url.database,
        )
        if remaining != 0:
            raise RuntimeError("Test database cleanup failed")


@contextmanager
def disposable_database() -> Iterator[URL]:
    url = ADMIN_URL.set(database=f"chathat_test_{uuid4().hex}")
    require_test_url(url)
    created = False

    async def create() -> None:
        nonlocal created

        async with admin_connection() as connection:
            await connection.execute(
                f'CREATE DATABASE "{url.database}" TEMPLATE template0'
            )
            created = True

    try:
        asyncio.run(create())
        yield url
    finally:
        if created:
            asyncio.run(drop_test_database(url))


def migrate(
    url: URL,
    revision: str,
    *,
    downgrade: bool = False,
) -> None:
    require_test_url(url)
    config = AlembicConfig("/app/alembic.ini")
    config.attributes["database_url"] = url

    if downgrade:
        command.downgrade(config, revision)
    else:
        command.upgrade(config, revision)


@asynccontextmanager
async def database_resources(url: URL) -> AsyncGenerator[Database]:
    require_test_url(url)
    database = create_database(SecretStr(url.render_as_string(hide_password=False)))
    try:
        yield database
    finally:
        await database.engine.dispose()
