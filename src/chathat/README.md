# ChatHat source map

Last completed lesson **P01-I02 — Dockerfile and development Compose foundation**. [Progress tracker](../../docs/progress-documentation/phase_1.md) · [Phase 01 notes](../../docs/progress-documentation/phase-01-notes.md)

| File | Read it for |
| --- | --- |
| [`src/chathat/main.py`](main.py) | `create_app()` assembles the app from core. The installed Uvicorn entry point is `chathat.main:create_app`. |
| [`core/routes/health.py`](core/routes/health.py) | Health router. Returns HTTP 200 after startup and HTTP 503 when the startup flag is absent or false. |
| [`core/schemas/health.py`](core/schemas/health.py) | `HealthResponse` defines the successful health response schema. |
| [`core/application/lifespan.py`](core/application/lifespan.py) | Sets and clears `app.state.started`. [Application setup notes](core/application/README.md) |
| [`src/chathat/__init__.py`](__init__.py), [`core/__init__.py`](core/__init__.py), [`core/tests/__init__.py`](core/tests/__init__.py) | Package markers. |
| [`core/tests/test_app.py`](core/tests/test_app.py) | Five in-process API tests for health and routing, app state isolation, lifespan, and startup failure. |
| [`pyproject.toml`](../../pyproject.toml), [`uv.lock`](../../uv.lock) | Python 3.12+, the `uv_build` backend, runtime dependencies, and the `pytest` and `httpx2` development dependencies. |
| [`dockerfiles/Dockerfile.api`](../../dockerfiles/Dockerfile.api) | Builds the API image with locked dependencies and runs the factory as a non-root user. |
| [`compose.yaml`](../../compose.yaml), [`compose.dev.yaml`](../../compose.dev.yaml) | API service, health check, default project network, development source mount, reload, and loopback port. |
| [`.dockerignore`](../../.dockerignore), [`.env.example`](../../.env.example), [`commands.txt`](../../commands.txt) | Build exclusions, host-port example, and development Compose commands. |

Next lesson **P01-T02 — Dockerized FastAPI and Compose configuration**. [Implementation plan](../../docs/chathat-implementation-plan.md#p01-t02--test-dockerized-fastapi-and-compose-configuration)
