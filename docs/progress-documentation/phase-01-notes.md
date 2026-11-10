# Phase 01 completion notes

This is the source of truth for Phase 01 lesson decisions, deviations, and verification evidence. Add a dated entry for each lesson and record completion once its acceptance checks pass. The [Phase 01 tracker](phase_1.md) provides the status overview.

## P01-I01 · FastAPI package and application factory

**Verified 2026-11-10.** The six implementation files and the initial notes matched the submitted diff before this update. [Original walkthrough](../lessons/phase-01-containerized-application-foundation/P01-I01-fastapi-package-and-application-factory.md)

### Implementation index

| Files | Responsibility |
| --- | --- |
| [`pyproject.toml`](../../pyproject.toml), [`uv.lock`](../../uv.lock) | Declare the build backend, Python and dependency requirements, and resolved dependency versions. |
| [`chathat/__init__.py`](../../src/chathat/__init__.py), [`chathat/api/__init__.py`](../../src/chathat/api/__init__.py) | Define the application and API packages under `src/`. |
| [`health.py`](../../src/chathat/api/health.py) | Defines the response schema and maps startup state to HTTP 200 or 503. |
| [`main.py`](../../src/chathat/main.py) | Registers the health router on each new app and owns the startup flag through lifespan. |

### Decisions from implementation

| Area | Decision |
| --- | --- |
| Packaging | Use uv for local dependency management and `uv_build` as the build backend. Keep the Python 3.12+ floor and `src/chathat/` layout. Record direct dependency minimums in `pyproject.toml` and resolved versions in `uv.lock`. Launch through Uvicorn, so the package has no generated `chathat` console script. |
| Health route | Rename the handler to `health` and declare `response_model=HealthResponse` explicitly while retaining the return annotation. The contract remains HTTP 200 with `{"status":"ok"}` during active lifespan and HTTP 503 with `{"detail":"Application unavailable"}` if a request reaches the handler without the startup flag. |
| Lifespan and factory | Annotate the lifespan with `AsyncGenerator[None]` and use FastAPI's default title. Each factory call still creates a fresh app. Lifespan sets the app's startup flag and clears it in `finally`. |
| Local launcher | The guarded reload launcher imports through `src.chathat.main:create_app`, which relies on the checkout being on the import path. The smoke check uses the installed package path `chathat.main:create_app` and an explicit factory flag. The guarded launcher remains unverified. |

### Verification

Using the existing `.venv`, Uvicorn reported successful startup and clean shutdown. `GET /health` returned HTTP 200 with `{"status":"ok"}` and a JSON content type. Repeating with `--lifespan off` returned HTTP 503 with `{"detail":"Application unavailable"}`. An in-process check confirmed that two factory calls have independent state, lifespan sets and clears the startup flag, and OpenAPI lists both response codes.

To reproduce the HTTP check from the repository root, use these commands. The verification used an OS-assigned loopback port. The example uses port 8000 so the URL is fixed.

```sh
.venv/bin/python -m uvicorn chathat.main:create_app --factory --lifespan on --host 127.0.0.1 --port 8000
# In a second terminal
curl -i http://127.0.0.1:8000/health
```

Stop the server with Ctrl+C to observe shutdown. Repeat with `--lifespan off` for the 503 branch.

## P01-T01 · Test the FastAPI package and application factory

**Completed 2026-11-10.** The submitted diff matches the checkout. [Lesson walkthrough](../lessons/phase-01-containerized-application-foundation/P01-T01-fastapi-package-and-application-factory.md)

- [tests/test_app.py](../../tests/test_app.py) covers HTTP 200 and 503 from `/health`, HTTP 404 for an unknown route, app state isolation through startup and shutdown, and startup exception propagation.
- [pyproject.toml](../../pyproject.toml) declares `pytest` and `httpx2` in the uv development group. [uv.lock](../../uv.lock) records their resolved versions.

The user's `pytest` run from the repository root collected five tests and reported **5 passed in 0.26s** on macOS with Python 3.12.7 and pytest 9.2.0.

Next is **P01-I02 — Dockerfile and development Compose foundation**.
