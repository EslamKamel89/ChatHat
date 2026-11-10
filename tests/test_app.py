from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, closing

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from chathat import main


@pytest.fixture
def app():
    return main.create_app()


def test_health_returns_ok_after_startup(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/health")
    assert response.status_code == 200
    assert response.headers["content-type"].split(";", 1)[0] == "application/json"
    assert response.json() == {"status": "ok"}


def test_unregistered_path_returns_404(app: FastAPI) -> None:
    with TestClient(app) as client:
        response = client.get("/missing")
    assert response.status_code == 404


def test_health_returns_unavailable_without_startup(app: FastAPI) -> None:
    with closing(TestClient(app)) as client:
        response = client.get("/health")
    assert response.status_code == 503
    assert response.json() == {"detail": "Application unavailable"}


def test_lifespan_changes_only_its_own_app(app: FastAPI) -> None:
    other_app = main.create_app()
    assert app is not other_app
    assert getattr(app.state, "started", False) is False
    with TestClient(app):
        assert app.state.started is True
        assert getattr(other_app.state, "started", False) is False
    assert app.state.started is False


def test_startup_error_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def initialize() -> None:
        raise RuntimeError("startup failed")

    @asynccontextmanager
    async def failing_lifespan(_: FastAPI) -> AsyncGenerator[None]:
        initialize()
        yield

    monkeypatch.setattr(main, "lifespan", failing_lifespan)
    app = main.create_app()

    with pytest.raises(RuntimeError, match="^startup failed$"):
        with TestClient(app):
            pytest.fail("The client entered despite a startup failure")
