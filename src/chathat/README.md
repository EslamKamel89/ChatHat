# ChatHat source map

Last completed lesson **P01-T07 — Verify feature-local test discovery and core behavior**. [Progress tracker](../../docs/progress-documentation/phase_1.md) · [Phase 01 notes](../../docs/progress-documentation/phase-01-notes.md)

| File | Read it for |
| --- | --- |
| [`src/chathat/main.py`](main.py) | `create_app()` assembles the app from core. The installed Uvicorn entry point is `chathat.main:create_app`. |
| [`core/routes/health.py`](core/routes/health.py) | Health router. Returns HTTP 200 after startup and HTTP 503 when the startup flag is absent or false. |
| [`core/schemas/health.py`](core/schemas/health.py) | `HealthResponse` defines the successful health response schema. |
| [`core/application/lifespan.py`](core/application/lifespan.py) | Sets and clears `app.state.started`. [Application setup notes](core/application/README.md) |
| [`src/chathat/__init__.py`](__init__.py), [`core/__init__.py`](core/__init__.py), [`core/tests/__init__.py`](core/tests/__init__.py) | Package markers. |
| [`core/tests/test_app.py`](core/tests/test_app.py) | Five in-process API tests for health and routing, app state isolation, lifespan, and startup failure. |
| [`pyproject.toml`](../../pyproject.toml), [`uv.lock`](../../uv.lock) | Python 3.12+, the `uv_build` backend, runtime dependencies, and the `pytest` and `httpx2` development dependencies. |

Next lesson **P01-I02 — Dockerfile and development Compose foundation**. [Implementation plan](../../docs/chathat-implementation-plan.md#p01-i02--implement-dockerfile-and-development-compose-foundation)
