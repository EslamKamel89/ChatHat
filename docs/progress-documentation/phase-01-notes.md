# Phase 01 completion notes

This is the source of truth for Phase 01 lesson decisions, deviations, and verification evidence. Add a dated entry for each lesson and record completion once its acceptance checks pass. The [Phase 01 tracker](phase_1.md) provides the status overview.

## P01-I01 · FastAPI package and application factory

**Verified 2026-11-10.** The six implementation files and the initial notes matched the submitted diff before this update.

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

**Completed 2026-11-10.** The submitted diff matches the checkout.

- [tests/test_app.py](../../tests/test_app.py) covers HTTP 200 and 503 from `/health`, HTTP 404 for an unknown route, app state isolation through startup and shutdown, and startup exception propagation.
- [pyproject.toml](../../pyproject.toml) declares `pytest` and `httpx2` in the uv development group. [uv.lock](../../uv.lock) records their resolved versions.

The user's `pytest` run from the repository root collected five tests and reported **5 passed in 0.26s** on macOS with Python 3.12.7 and pytest 9.2.0.

## P01-I07 · Organize the application foundation by feature

**Completed 2026-11-14.** Reviewed the working-tree refactor and recorded the user's repository-root `pytest` output. It collected the five tests from `src/chathat/core/tests/test_app.py` and reported **5 passed in 0.20s**, using Python 3.12.7 and pytest 9.2.0 on macOS.

| File | Reviewed change |
| --- | --- |
| [core/routes/health.py](../../src/chathat/core/routes/health.py) | Moved the original health router and response schema together. |
| [core/application/lifespan.py](../../src/chathat/core/application/lifespan.py) | Extracted the existing startup and shutdown implementation. |
| [main.py](../../src/chathat/main.py) | Imports the core router and lifespan while keeping `create_app()` as the entry point. |
| [core/tests/test_app.py](../../src/chathat/core/tests/test_app.py) | Moved all five tests without changing their contents. The startup failure test still patches `main.lifespan`, the name resolved by the factory. |
| [core/application/README.md](../../src/chathat/core/application/README.md) | Describes application setup responsibilities. |

The original API source package and root test file were removed. The historical P01-I01 and P01-T01 entries above describe their original locations.

The initial refactor kept `HealthResponse` in the health route module and placed lifespan under `core/application/`. On 2026-11-14, moved `HealthResponse` to [core/schemas/health.py](../../src/chathat/core/schemas/health.py) and updated the route import to follow specification §2.2. Lifespan remains in `core/application/lifespan.py`, which differs from the specification and plan's `core/lifespan.py` path.

After extracting the schema, ran `.venv/bin/python -m pytest -q src/chathat/core/tests` and observed **5 passed in 0.21s**.

## P01-T07 · Verify feature-local test discovery and core behavior

**Completed 2026-11-14.** The user confirmed completion and supplied console evidence for discovery, execution, and the Uvicorn health response.

| Command | Supplied result |
| --- | --- |
| `uv run --locked pytest --collect-only -q src/chathat/core/tests` | The five expected tests collected in 0.15s. |
| `uv run --locked pytest --collect-only -q` | The same five tests collected in 0.11s. |
| `uv run --locked pytest -q src/chathat/core/tests` | 5 passed in 0.12s. |
| `uv run --locked pytest -q` | 5 passed in 0.13s. |
| `curl -i http://127.0.0.1:8000/health` | HTTP 200 from Uvicorn with `application/json` and `{"status":"ok"}`. |

The evidence verifies discovery from the repository root and core feature directory, the five existing behavior contracts, and the running application's health endpoint. The supplied excerpt contains the HTTP response alongside the user's confirmation that the previous step is complete.

## P01-I02 · Dockerfile and development Compose foundation

**Completed 2026-11-15.** Reviewed the working-tree implementation and the user's confirmation of completion. The supplied containerized pytest output reports **5 passed in 0.37s** on Linux with Python 3.12.7 and pytest 9.2.0. All five tests were discovered under `src/chathat/core/tests/test_app.py`.

| File | Implementation |
| --- | --- |
| [dockerfiles/Dockerfile.api](../../dockerfiles/Dockerfile.api) | Python 3.12.7 and uv 0.13.7 image inputs, non-root user 10001, locked development dependencies, and installed Uvicorn factory entry point. Installs dependencies before copying source for build-cache reuse, then installs the project. |
| [.dockerignore](../../.dockerignore) | Excludes the host virtual environment, local environment files, caches, and runtime data from the build context. |
| [compose.yaml](../../compose.yaml) | Builds the API image using the relocated Dockerfile, supplies an init process and an HTTP health check, and uses Compose's default project network. |
| [compose.dev.yaml](../../compose.dev.yaml) | Enables source reload, a read-only source bind mount, and a loopback-bound configurable host port. |
| [.env.example](../../.env.example) | Documents `CHATHAT_DEV_PORT=8000`. |
| [commands.txt](../../commands.txt) | Records development startup, containerized pytest, and shutdown commands. |
| [main.py](../../src/chathat/main.py) | Removes the guarded development launcher. The installed `chathat.main:create_app` factory is used by Docker. |

The submitted command `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest` passed. The supplied `down` output confirms removal of `chathat-api-1` and `chathat_default`. A review-time `docker compose -f compose.yaml -f compose.dev.yaml config --quiet` also exited successfully.

The Dockerfile lives under `dockerfiles/`, and the service uses Compose's default network in place of the walkthrough's explicit `backend` network. Compose still scopes that network to the project. The console excerpt verifies pytest and shutdown. Health-check and reload configuration were inspected in source, with runtime completion reported by the user.

## P01-T02 · Implementation and verification

**Verified 2026-11-15.** Added [test_container.py](../../src/chathat/core/tests/test_container.py) with three tests covering the Compose source configuration, real Uvicorn health response, and non-root Python environment with installed dependencies. PyYAML is a locked development dependency. The image includes both Compose files so the fixture reads them automatically.

The standard command is `pytest` inside the running API container, after normal development startup. No test-specific environment variables or generated configuration files are required.

Built and started the service with `docker compose -f compose.yaml -f compose.dev.yaml up --build -d --wait`. Ran `docker compose -f compose.yaml -f compose.dev.yaml exec -T api pytest` and observed **8 passed in 1.20s**. Restarted and recreated the service, waited for health, and repeated the same pytest command with **8 passed in 1.38s**.

Also validated the rendered Compose JSON for reload, loopback port binding, and the read-only source mount. This was a separate review check. The pytest configuration test reads the two YAML source files and does not exercise Compose's merge engine. Runtime reload after editing source was not checked in this run.

**Completed 2026-11-15.** Reviewed the current diff and recorded the user's confirmation that all tests passed. The implementation includes three container checks alongside the five existing application tests. The Dockerfile copies the Compose files into `/app`, and `pyproject.toml` plus `uv.lock` include PyYAML. Completion uses the user's test confirmation and the verification evidence recorded above.

Next is **P01-I03 — Nginx Compose service and internal routing**.
