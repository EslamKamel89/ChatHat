# P01-I01 · FastAPI package and application factory

**Objective** — Build an installable ChatHat package, a factory that creates a fresh FastAPI application, and a typed health route backed by the application's lifespan.

> The walkthrough below records the original teaching example. The checkout uses uv and `uv_build`. See the [Phase 01 notes](../../progress-documentation/phase-01-notes.md#p01-i01--fastapi-package-and-application-factory) for the implementation index and the verified run command.

At the start of this lesson, the checkout contained documentation and an empty lesson directory. The curriculum places the first Compose setup in P01-I02, so this lesson uses a temporary loopback-only demo. The phase's development environment uses Compose and Nginx once those services are introduced. [Implementation plan](../../chathat-implementation-plan.md#phase-01--containerized-application-foundation) · [Product specification, technology stack and infrastructure](../../chathat-spec.md#2-confirmed-technology-stack-and-engineering-constraints) · [Docker Compose infrastructure](../../chathat-spec.md#24-docker-compose--development-and-production-infrastructure)

## Contract

| Boundary | Expected behavior |
| --- | --- |
| `create_app()` | Takes no arguments and returns a new FastAPI instance with its own state and the health route registered. |
| Lifespan | Sets the instance's startup flag when entering lifespan and clears it on exit. An exception during startup propagates to the ASGI server, which fails startup. |
| `GET /health` | Takes no parameters or credentials. Returns HTTP 200 and `{"status":"ok"}` while the application's lifespan is active. |
| Health handler called outside lifespan | Returns HTTP 503 and `{"detail":"Application unavailable"}` if the request reaches the handler with startup state missing or false. |

The health response reports process startup only. It exposes a fixed status string and requires no database, credentials, or external services. During ordinary Uvicorn operation the server waits for successful startup before serving requests, so the 503 branch is easiest to exercise with an ASGI test client that deliberately skips lifespan.

## 1. Declare the package

Use Python 3.12 or newer for this walkthrough. From the repository root, create the package directories and two empty `__init__.py` files.

```sh
mkdir -p src/chathat/api
touch src/chathat/__init__.py src/chathat/api/__init__.py
```

Add `pyproject.toml` at the repository root.

```toml
[build-system]
requires = ["setuptools>=64"]
build-backend = "setuptools.build_meta"

[project]
name = "chathat"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi",
    "pydantic",
    "uvicorn",
]

[tool.setuptools.packages.find]
where = ["src"]
```

The build-system table tells pip to use Setuptools to build and install the project. The project table declares the runtime dependencies. FastAPI defines the application and HTTP contract, Pydantic defines the response schema, and Uvicorn runs the ASGI application and drives its lifespan. Declare Pydantic directly because the health module imports it. The `src` layout keeps the package off the default repository-root import path, so the demo exercises the installed package. The two `__init__.py` files declare regular Python packages. Reproducible container dependency installation belongs to P01-I02. [Python Packaging User Guide](https://packaging.python.org/en/latest/discussions/src-layout-vs-flat-layout/)

## 2. Define the typed health route

Add `src/chathat/api/health.py`.

```python
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: Literal["ok"]


@router.get("/health", responses={503: {"description": "Application unavailable"}})
async def get_health(request: Request) -> HealthResponse:
    if not getattr(request.app.state, "started", False):
        raise HTTPException(status_code=503, detail="Application unavailable")

    return HealthResponse(status="ok")
```

- `APIRouter` collects route definitions for the factory to attach to each application. Importing this module registers the handler with the router.
- FastAPI supplies `Request` from the current ASGI request. `request.app.state` reads state owned by that request's application instance. The default value of `False` makes a missing flag follow the same failure path as a cleared flag.
- FastAPI uses the return annotation as the successful response model. `Literal["ok"]` makes the allowed success value explicit in both validation and the generated schema. Raising `HTTPException` takes the error path, which is also listed in the OpenAPI responses.
- The handler is asynchronous and does only a small in-memory read. It needs no request-scoped dependency such as a database session. [FastAPI response models](https://fastapi.tiangolo.com/tutorial/response-model/)

## 3. Create the lifespan and factory

Start `src/chathat/main.py` with the lifespan function.

```python
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from chathat.api.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    app.state.started = True
    try:
        yield
    finally:
        app.state.started = False
```

`@asynccontextmanager` lets FastAPI enter the function at startup and exit it at shutdown. Code before `yield` runs before serving requests. The function stays suspended at `yield` while requests are served. The `finally` block clears the flag when the context exits, including when exit carries an exception. Future startup work would need to succeed before setting `started`. Each running application instance owns its own flag, including separate instances in separate worker processes. [FastAPI lifespan events](https://fastapi.tiangolo.com/advanced/events/)

Append the factory to the same file.

```python


def create_app() -> FastAPI:
    app = FastAPI(title="ChatHat", lifespan=lifespan)
    app.include_router(health_router)
    return app
```

Calling the factory constructs the application and attaches routes. The ASGI server then drives startup, and the router dispatches individual requests. A module-level application would also serve requests, but a factory lets tests build fresh instances for separate lifespan runs without sharing application state.

## 4. Run the demo

From the repository root, create an isolated Python environment, install the project in editable mode, and start Uvicorn. Editable mode lets the installed package import from `src/` as you edit it. The `--factory` flag tells Uvicorn to call `create_app`, and `--lifespan on` enables the startup and shutdown protocol.

```sh
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m uvicorn chathat.main:create_app --factory --lifespan on --host 127.0.0.1 --port 8000
```

In a second terminal, send a request.

```sh
curl -i http://127.0.0.1:8000/health
```

**Expected result** — Uvicorn reports successful startup. The request returns HTTP 200 with a JSON content type and the body `{"status":"ok"}`. Stop Uvicorn with Ctrl+C and look for its application shutdown completion message. If the import fails, check that you installed the package with the same virtual environment interpreter from the directory containing `pyproject.toml`. If port 8000 is busy, choose another free port in both commands.

## Checkpoint

- The increment consists of `pyproject.toml`, the two `__init__.py` files, `src/chathat/api/health.py`, and `src/chathat/main.py`.
- Confirm that the package imports through Uvicorn, startup succeeds, the health response matches the contract, and shutdown completes. [Verification for the uv implementation](../../progress-documentation/phase-01-notes.md#verification)
- Next is **P01-T01**, the separate pytest lesson for route behavior, instance isolation, lifespan startup and shutdown, and startup failure. Continue to P01-I02 after the paired tests pass. [Phase 01 tracker](../../progress-documentation/phase_1.md)
