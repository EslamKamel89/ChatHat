# P01-T01 · Test the FastAPI package and application factory

**Objective** — Verify that the FastAPI factory registers the health route, keeps startup state local to each application, and surfaces startup failures.

P01-I01 is complete and its smoke check is recorded. The checkout has `create_app()`, `lifespan()`, and `GET /health`, plus a uv-managed Python 3.12+ package. This is the first pytest suite. Compose arrives in P01-I02, so run this lesson through uv in the project environment. The spec's INFRA-005 requirement for containerized pytest applies once the application container exists. [Implementation plan](../../chathat-implementation-plan.md#p01-t01--test-fastapi-package-and-application-factory) · [P01-I01 verification](../../progress-documentation/phase-01-notes.md#verification)

## Contract and test strategy

| Case | Expected result |
| --- | --- |
| `GET /health` after startup | HTTP 200, JSON content type, and `{"status":"ok"}`. |
| `GET /health` without running lifespan | HTTP 503 and `{"detail":"Application unavailable"}`. |
| Unregistered path | HTTP 404. |
| Two factory calls | Independent instances and state. Starting one leaves the other untouched. Shutdown clears the started instance's flag. |
| Startup raises an exception | The client fails while entering lifespan and surfaces the exception. |

Use in-process API tests with FastAPI's `TestClient`. They exercise the actual router, serialization, and lifespan without opening a TCP port or needing Uvicorn. Keep one function-scoped app fixture, and let each test decide whether to enter lifespan. For the startup failure, inject a failing lifespan only in that test, since the current app has no external startup dependency to make fail. [FastAPI lifespan testing](https://fastapi.tiangolo.com/advanced/testing-events/)

## 1. Add development dependencies and an app fixture

From the repository root, run the following commands. `uv add --dev` adds the test dependencies to the development group in `pyproject.toml` and resolves them in `uv.lock`. The installed Starlette 1.10.0 `TestClient` prefers `httpx2` as its HTTP client dependency. [uv development dependencies](https://docs.astral.sh/uv/concepts/projects/dependencies/#development-dependencies)

```sh
uv add --dev pytest httpx2
mkdir -p tests
```

Start `tests/test_app.py` with these imports and the fixture. Append the remaining snippets to the same file in order.

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager, closing

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from chathat import main


@pytest.fixture
def app() -> FastAPI:
    return main.create_app()
```

Pytest injects this fixture into tests that declare an `app` parameter. Its default function scope creates a fresh app for each test, which keeps state changes from leaking across tests. The fixture only constructs the app. Lifespan begins when a test enters `with TestClient(app)` and ends when it leaves the block.

## 2. Verify HTTP routing and the success response

```python
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
```

The first test confirms that the factory wires up the route and that FastAPI serializes its response with the expected media type and body. Splitting the header allows a media-type parameter such as a charset. The second test checks the routing boundary. A missing URL should yield 404 instead of being handled by a catch-all route.

## 3. Verify the unavailable response

```python
def test_health_returns_unavailable_without_startup(app: FastAPI) -> None:
    with closing(TestClient(app)) as client:
        response = client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"detail": "Application unavailable"}
```

`closing(...)` calls the client's `close()` at exit without entering the client's own context manager, so this request reaches the route with the startup flag absent. The assertions verify the exact failure contract. This deliberately skips lifespan in the test harness. During normal operation Uvicorn waits for successful startup before serving requests.

## 4. Verify lifespan and factory isolation

```python
def test_lifespan_changes_only_its_own_app(app: FastAPI) -> None:
    other_app = main.create_app()

    assert app is not other_app
    assert getattr(app.state, "started", False) is False

    with TestClient(app):
        assert app.state.started is True
        assert getattr(other_app.state, "started", False) is False

    assert app.state.started is False
```

The identity check catches a factory that returns a shared instance. The assertions around the context block show the lifecycle transition from inactive to active and back. Checking the second app while the first is active catches accidental shared startup state.

## 5. Verify a startup exception reaches the caller

```python
def test_startup_error_propagates(monkeypatch: pytest.MonkeyPatch) -> None:
    def initialize() -> None:
        raise RuntimeError("startup failed")

    @asynccontextmanager
    async def failing_lifespan(_: FastAPI) -> AsyncIterator[None]:
        initialize()
        yield

    monkeypatch.setattr(main, "lifespan", failing_lifespan)
    app = main.create_app()

    with pytest.raises(RuntimeError, match="^startup failed$"):
        with TestClient(app):
            pytest.fail("The client entered despite a startup failure")
```

The factory reads `main.lifespan` when it constructs the app, so apply the patch before calling `create_app()`. In the injected context, initialization fails before `yield`. The matching exception proves that the failure surfaces when the client enters lifespan, before any request can run. Pytest restores the original lifespan when the test ends. [pytest monkeypatch fixture](https://docs.pytest.org/en/stable/how-to/monkeypatch.html)

## Run and record the result

From the repository root, run the focused suite and then the full suite.

```sh
uv run --locked pytest -q tests/test_app.py
uv run --locked pytest -q
```

**Expected result** — Both commands report **5 passed** in a checkout with just this suite. The snippets are proposed and the test results are unverified. If `TestClient` fails to import, check that the development dependencies were added and that uv is running in the project environment. If the success case returns 503, check that the request runs inside `with TestClient(app)`.

Once both commands pass, record the observed result in the [Phase 01 notes](../../progress-documentation/phase-01-notes.md) and propose marking P01-T01 complete in the [tracker](../../progress-documentation/phase_1.md). The next lesson is **P01-I02 — Dockerfile and development Compose foundation**.
