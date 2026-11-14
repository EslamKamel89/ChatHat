# P01-I07 · Organize the application foundation by feature

Move the existing application foundation into `core/`, including its tests. This implements TECH-014 and prepares the package structure for upcoming features such as authentication.

P01-I01 and P01-T01 are recorded as complete. The checkout currently has health in `src/chathat/api/health.py`, lifespan in `src/chathat/main.py`, and five tests in `tests/test_app.py`. The root README still describes a documentation-only project. The source and progress tracker show the implemented foundation. [Specification §2.2](../../chathat-spec.md#22-feature-packages) · [Implementation plan](../../chathat-implementation-plan.md#p01-i07--implement-organize-the-application-foundation-by-feature) · [Progress tracker](../../progress-documentation/phase_1.md)

## Contract

| Boundary       | Acceptance criterion                                                                                                                                |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Entry point    | `chathat.main:create_app` creates a fresh FastAPI application.                                                                                      |
| Health         | Active lifespan yields HTTP 200 with `{"status":"ok"}`. Missing or false startup state yields HTTP 503 with `{"detail":"Application unavailable"}`. |
| Lifespan       | Startup sets the app's own flag. Shutdown clears it. Startup exceptions propagate.                                                                  |
| Routing        | An unknown path returns HTTP 404.                                                                                                                   |
| Test ownership | The same five tests reside in `src/chathat/core/tests/test_app.py` and are discoverable from the repository root.                                   |

This refactor changes module paths. Application state still belongs to each app instance. Each Uvicorn process constructs its own app and runs its lifespan.

## 1. Move health and the existing tests

Run from the repository root.

```sh
mkdir -p src/chathat/core/tests
touch src/chathat/core/__init__.py src/chathat/core/tests/__init__.py
mv src/chathat/api/health.py src/chathat/core/health.py
mv tests/test_app.py src/chathat/core/tests/test_app.py
```

The health module moves with its router and response schema. Its handler continues to read `request.app.state.started` from the app handling the request. The tests retain their fixture and five assertions-based test cases.

The empty `__init__.py` files establish regular Python packages. Giving each feature's test directory a package identity also supports distinct test module paths as more features gain a `test_app.py` or other repeated filename.

## 2. Extract lifespan into core

Create `src/chathat/core/lifespan.py` with the existing lifecycle implementation.

```python
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.started = True
    try:
        yield
    finally:
        app.state.started = False
```

The async context manager sets the flag when the server enters lifespan, suspends at `yield` while requests run, and clears the flag when the context exits. The `finally` block also runs when the exit carries an exception. Importing this module defines the function. The server or test client enters the lifecycle later.

## 3. Assemble the app from its feature

Replace the imports and local lifespan definition in `src/chathat/main.py`. After the edit, the complete file should be as follows.

```python
from fastapi import FastAPI

from chathat.core.health import router as health_router
from chathat.core.lifespan import lifespan


def create_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.include_router(health_router)
    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.chathat.main:create_app", host="127.0.0.1", port=8000, reload=True)
```

The factory assembles the app from the core feature. Core modules import FastAPI and their own dependencies. Keeping that dependency direction avoids a circular import in which core imports the factory while the factory is importing core.

Read the startup failure test in `src/chathat/core/tests/test_app.py`. It imports `main` and calls `monkeypatch.setattr(main, "lifespan", failing_lifespan)` before creating an app. This still targets the correct name. The import above binds `lifespan` in `main`, and `create_app()` looks up that name when called.

## 4. Remove the old package marker

After checking that `src/chathat/api/__init__.py` is empty and the health module has moved, delete that empty file in your editor. Check the source for imports of the old package.

```sh
rg -n 'chathat\.api' src/chathat
```

Expect zero matches. Ripgrep exits with status 1 when a search finds no matches. An empty directory can still contain generated `__pycache__` files. The tracked package is removed once its source files are gone.

The resulting source files should have this structure.

```text
src/chathat/
├── __init__.py
├── README.md
├── main.py
└── core/
    ├── __init__.py
    ├── health.py
    ├── lifespan.py
    └── tests/
        ├── __init__.py
        └── test_app.py
```

## 5. Demonstrate the installed entry point

Compose setup follows this refactor pair. For this demonstration, start the installed app through the existing uv environment from the repository root.

```sh
uv run --locked uvicorn chathat.main:create_app --factory --lifespan on --host 127.0.0.1 --port 8000
```

In another terminal, request health.

```sh
curl -i http://127.0.0.1:8000/health
```

Expect successful startup and HTTP 200 with `{"status":"ok"}`. Stop Uvicorn with Ctrl+C and expect application shutdown to complete. If an import fails, check the core package marker and the two new imports in `main.py`. If the port is occupied, choose a free port in both commands.

## Review and paired testing

The affected files are the moved health module, extracted lifespan module, updated factory imports, moved test suite, two new core package markers, and removed API package marker. The HTTP response contract and application instance lifecycle are the acceptance boundaries.

Next is **P01-T07 — Verify feature-local test discovery and core behavior**. It runs both commands below and checks that each collects and passes the same five tests.

```sh
uv run --locked pytest -q src/chathat/core/tests
uv run --locked pytest -q
```

The walkthrough is proposed code. Runtime and pytest results for this refactor are pending. After verification, record the new file paths and evidence in the phase notes, refresh the source map, and propose the corresponding tracker updates. Then continue to P01-I02. [Phase notes](../../progress-documentation/phase-01-notes.md) · [Source map](../../../src/chathat/README.md)
