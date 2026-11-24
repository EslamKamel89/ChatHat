import asyncio
from collections.abc import Iterator

import pytest
from alembic.config import Config as AlembicConfig
from alembic.script import ScriptDirectory
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import event, text
from sqlalchemy.engine import URL
from sqlalchemy.exc import IntegrityError

from chathat.core.application.state import get_app_state
from chathat.core.dependencies.database import SessionDependency
from chathat.core.settings.config import Config
from chathat.core.tests.database.support import (
    ADMIN_URL,
    admin_connection,
    database_resources,
    disposable_database,
    execute,
    migrate,
    require_test_url,
    restart_test_database,
    scalar,
)
from chathat.main import create_app

PROBE_TABLE = """
CREATE TABLE probe (
    id integer PRIMARY KEY,
    label text NOT NULL UNIQUE,
    score integer NOT NULL CHECK (score >= 0)
)
"""

INSERT_PROBE = text("INSERT INTO probe (id, label, score) VALUES (:id, :label, :score)")


@pytest.fixture
def database_url() -> Iterator[URL]:
    with disposable_database() as url:
        yield url


@pytest.fixture
def migrated_url(database_url: URL) -> URL:
    migrate(database_url, "head")
    return database_url


@pytest.fixture
def prepared_url(migrated_url: URL) -> URL:
    asyncio.run(execute(migrated_url, PROBE_TABLE))
    return migrated_url


@pytest.mark.parametrize(
    "changes",
    [
        {"host": "db"},
        {"host": "production.example"},
        {"database": "chathat"},
        {"database": "postgres"},
        {"username": "chathat"},
        {"drivername": "postgresql"},
        {"query": {"host": "db"}},
    ],
)
def test_database_guard_rejects_unsafe_targets(changes: dict) -> None:
    valid = ADMIN_URL.set(database="chathat_test_" + "a" * 32)
    require_test_url(valid)

    with pytest.raises(ValueError, match="non-isolated"):
        require_test_url(valid.set(**changes))


@pytest.mark.parametrize("fail_inside", [False, True])
def test_database_cleanup_runs_after_success_or_failure(
    fail_inside: bool,
) -> None:
    url: URL | None = None

    def exercise() -> None:
        nonlocal url

        with disposable_database() as created_url:
            url = created_url
            assert (
                asyncio.run(scalar(created_url, "SELECT current_database()"))
                == created_url.database
            )

            if fail_inside:
                raise RuntimeError("simulated test failure")

    if fail_inside:
        with pytest.raises(RuntimeError, match="simulated test failure"):
            exercise()
    else:
        exercise()

    assert url is not None

    async def remaining_databases() -> int:
        async with admin_connection() as connection:
            return await connection.fetchval(
                "SELECT count(*) FROM pg_database WHERE datname = $1",
                url.database,  # type: ignore
            )  # type: ignore

    assert asyncio.run(remaining_databases()) == 0


def test_migration_upgrade_downgrade_and_reupgrade(
    database_url: URL,
    head_revision: str,
) -> None:
    extension_query = "SELECT extversion FROM pg_extension WHERE extname = 'vector'"

    assert asyncio.run(scalar(database_url, extension_query)) is None

    migrate(database_url, "head")
    migrate(database_url, "head")

    assert (
        asyncio.run(scalar(database_url, "SELECT version_num FROM alembic_version"))
        == head_revision
    )
    assert asyncio.run(scalar(database_url, extension_query)) is not None
    assert (
        asyncio.run(
            scalar(
                database_url,
                "SELECT '[1,2,3]'::vector <-> '[1,2,3]'::vector",
            )
        )
        == 0
    )

    migrate(database_url, "base", downgrade=True)

    assert asyncio.run(scalar(database_url, extension_query)) is None
    assert (
        asyncio.run(scalar(database_url, "SELECT count(*) FROM alembic_version")) == 0
    )

    migrate(database_url, "head")

    assert (
        asyncio.run(scalar(database_url, "SELECT version_num FROM alembic_version"))
        == head_revision
    )


def test_databases_do_not_share_application_tables(
    prepared_url: URL,
) -> None:
    assert (
        asyncio.run(scalar(prepared_url, "SELECT to_regclass('public.probe')::text"))
        == "probe"
    )

    with disposable_database() as other_url:
        assert other_url.database != prepared_url.database
        assert (
            asyncio.run(scalar(other_url, "SELECT to_regclass('public.probe')::text"))
            is None
        )


@pytest.mark.parametrize(
    ("row", "sqlstate"),
    [
        ({"id": 1, "label": "other", "score": 1}, "23505"),
        ({"id": 2, "label": "baseline", "score": 1}, "23505"),
        ({"id": 2, "label": None, "score": 1}, "23502"),
        ({"id": 2, "label": "negative", "score": -1}, "23514"),
    ],
)
def test_constraints_rollback_failed_transactions(
    prepared_url: URL,
    row: dict,
    sqlstate: str,
) -> None:
    async def scenario() -> None:
        async with database_resources(prepared_url) as database:
            async with database.sessions() as session:
                async with session.begin():
                    await session.execute(
                        INSERT_PROBE,
                        {"id": 1, "label": "baseline", "score": 1},
                    )

                with pytest.raises(IntegrityError) as caught:
                    async with session.begin():
                        await session.execute(INSERT_PROBE, row)

                assert caught.value.orig.sqlstate == sqlstate  # type: ignore

                async with session.begin():
                    assert await session.scalar(text("SELECT count(*) FROM probe")) == 1

    asyncio.run(scenario())


def test_rollback_close_and_committed_reconnection(
    prepared_url: URL,
) -> None:
    async def scenario() -> None:
        async with database_resources(prepared_url) as database:
            async with database.sessions() as session:
                with pytest.raises(RuntimeError, match="abort operation"):
                    async with session.begin():
                        await session.execute(
                            INSERT_PROBE,
                            {"id": 1, "label": "aborted", "score": 1},
                        )
                        raise RuntimeError("abort operation")

            async with database.sessions() as session:
                await session.execute(
                    INSERT_PROBE,
                    {"id": 2, "label": "unfinished", "score": 1},
                )

            async with database.sessions() as session:
                async with session.begin():
                    assert await session.scalar(text("SELECT count(*) FROM probe")) == 0

                    await session.execute(
                        INSERT_PROBE,
                        {"id": 3, "label": "committed", "score": 1},
                    )

        async with database_resources(prepared_url) as replacement:
            async with replacement.sessions() as session:
                assert (
                    await session.scalar(text("SELECT label FROM probe")) == "committed"
                )

    asyncio.run(scenario())


def test_committed_data_survives_test_database_container_restart(
    prepared_url: URL,
    head_revision: str,
) -> None:
    async def scenario() -> None:
        async with database_resources(prepared_url) as database:
            async with database.sessions() as session:
                async with session.begin():
                    await session.execute(
                        INSERT_PROBE,
                        {"id": 1, "label": "survives-container-restart", "score": 7},
                    )

        before, after = await restart_test_database(prepared_url)
        assert after != before

        async with database_resources(prepared_url) as replacement:
            async with replacement.sessions() as session:
                row = (
                    await session.execute(text("SELECT id, label, score FROM probe"))
                ).one()
                assert tuple(row) == (1, "survives-container-restart", 7)
                assert (
                    await session.scalar(
                        text("SELECT version_num FROM alembic_version")
                    )
                    == head_revision
                )
                assert (
                    await session.scalar(
                        text("SELECT '[1,2,3]'::vector <-> '[1,2,3]'::vector")
                    )
                    == 0
                )

    asyncio.run(scenario())


def test_request_sessions_and_lifespan_cleanup(
    prepared_url: URL,
) -> None:
    app = create_app(
        config=Config(
            environment="test",
            debug=False,
            secret_key=None,
            database_url=SecretStr(prepared_url.render_as_string(hide_password=False)),
        )
    )
    database = get_app_state(app).database
    assert database is not None

    closed_connections: list[bool] = []

    def connection_closed(connection: object, record: object) -> None:
        closed_connections.append(True)

    event.listen(database.engine.sync_engine, "close", connection_closed)

    @app.post("/_test/write/{mode}")
    async def write(mode: str, session: SessionDependency) -> dict[str, str]:
        rows = {
            "commit": {"id": 1, "label": "committed", "score": 1},
            "abort": {"id": 2, "label": "aborted", "score": 1},
            "unfinished": {"id": 3, "label": "unfinished", "score": 1},
        }

        if mode == "unfinished":
            await session.execute(INSERT_PROBE, rows[mode])
            return {"status": mode}

        async with session.begin():
            await session.execute(INSERT_PROBE, rows[mode])
            if mode == "abort":
                raise HTTPException(status_code=409, detail="abort operation")

        return {"status": mode}

    try:
        with TestClient(app) as client:
            assert client.post("/_test/write/commit").status_code == 200
            assert client.post("/_test/write/abort").status_code == 409
            assert client.post("/_test/write/unfinished").status_code == 200

        assert app.state.started is False
        assert closed_connections

        assert asyncio.run(scalar(prepared_url, "SELECT count(*) FROM probe")) == 1
        assert (
            asyncio.run(scalar(prepared_url, "SELECT label FROM probe")) == "committed"
        )
    finally:
        event.remove(
            database.engine.sync_engine,
            "close",
            connection_closed,
        )


def test_database_dependency_returns_503_without_resources() -> None:
    app = create_app(
        config=Config(
            environment="test",
            debug=False,
            secret_key=None,
            database_url=None,
        )
    )

    @app.get("/_test/database")
    async def database_route(
        session: SessionDependency,
    ) -> dict[str, bool]:
        return {"connected": True}

    with TestClient(app) as client:
        response = client.get("/_test/database")

    assert response.status_code == 503
    assert response.json() == {"detail": "Database unavailable"}


@pytest.fixture
def head_revision() -> str:
    script = ScriptDirectory.from_config(AlembicConfig("/app/alembic.ini"))
    revision = script.get_current_head()
    assert revision is not None
    return revision
