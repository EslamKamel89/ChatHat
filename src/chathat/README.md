# ChatHat source map

Last completed lesson **P01-T01 — Test the FastAPI package and application factory**. [Progress tracker](../../docs/progress-documentation/phase_1.md) · [Phase 01 notes](../../docs/progress-documentation/phase-01-notes.md)

| File | Read it for |
| --- | --- |
| [`src/chathat/main.py`](main.py) | `create_app()` builds a fresh FastAPI instance and registers the health router. `lifespan()` sets and clears `app.state.started`. The installed Uvicorn entry point is `chathat.main:create_app`. |
| [`src/chathat/api/health.py`](api/health.py) | `health()` handles `GET /health`. It returns HTTP 200 with `{"status":"ok"}` after startup and HTTP 503 when the startup flag is absent or false. `HealthResponse` defines the success schema. |
| [`src/chathat/__init__.py`](__init__.py), [`src/chathat/api/__init__.py`](api/__init__.py) | Package markers. |
| [`tests/test_app.py`](../../tests/test_app.py) | In-process API tests for health and routing, app state isolation, lifespan, and startup failure. |
| [`pyproject.toml`](../../pyproject.toml), [`uv.lock`](../../uv.lock) | Python 3.12+, the `uv_build` backend, runtime dependencies, and the `pytest` and `httpx2` development dependencies. |

Next lesson **P01-I02 — Dockerfile and development Compose foundation**.
