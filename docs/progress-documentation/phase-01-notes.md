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


## P01-I03 · Nginx Compose service and internal routing

**Completed 2026-11-15.** Reviewed the current working-tree diff and both new files under `nginx/` against P01-I03 and INFRA-006. No blocking implementation issues were found. Runtime evidence below was supplied by the user; commands were not rerun during this documentation update.

| File | Reviewed implementation |
| --- | --- |
| [compose.yaml](../../compose.yaml) | Adds `nginx:1.28-alpine`, API-health startup dependency, read-only configuration/static mounts, and a health check through Nginx to FastAPI. Configures the default network as `172.30.0.0/24` with Nginx at `172.30.0.10`. |
| [compose.dev.yaml](../../compose.dev.yaml) | Moves the loopback host-port publication from API port 8000 to Nginx port 80. Preserves API reload and the read-only source mount; enables proxy headers trusted only from `172.30.0.10`. |
| [dockerfiles/Dockerfile.api](../../dockerfiles/Dockerfile.api) | Adds the same explicit proxy-header trust to the default Uvicorn command. |
| [nginx/default.conf](../../nginx/default.conf) | Routes to `api:8000` using Docker DNS and dynamic upstream resolution; serves `/static/` directly; replaces forwarding headers; sets a 10 MiB body ceiling, 5-second connect timeout, 75-second read/send timeouts, and disables proxy response buffering/cache. |
| [nginx/static/site.css](../../nginx/static/site.css) | Supplies the initial public static asset. |
| [core/tests/test_container.py](../../src/chathat/core/tests/test_container.py) | Updates the existing Compose source assertion for Nginx port publication and absence of API port publication. The runtime API-health test still addresses Uvicorn directly. |

### Supplied verification evidence

| Command | User-supplied result |
| --- | --- |
| `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest` | **8 passed in 1.19s**, Python 3.12.7 and pytest 9.2.0 on Linux; five application tests and three container tests. |
| `docker ps` and `docker compose -f compose.yaml -f compose.dev.yaml ps` | Both API and Nginx healthy. Only Nginx publishes `127.0.0.1:8000->80/tcp`; API shows `8000/tcp` without a host mapping. |
| `curl -i http://127.0.0.1:8000/health` | HTTP 200, `application/json`, `{"status":"ok"}`, served through Nginx 1.28.3. |
| `curl -i http://127.0.0.1:8000/static/site.css` | HTTP 200, `text/css`, expected CSS contents. |
| `curl -i http://127.0.0.1:8000/missing` | HTTP 404, `application/json`, `{"detail":"Not Found"}` through Nginx. |

### Decisions and verification boundaries

- Nginx's fixed address and both Uvicorn trust settings must remain aligned. The chosen subnet must not overlap other Docker networks or host/VPN routes.
- The 10 MiB request-body ceiling is provisional infrastructure configuration, not a finalized document-upload policy. Buffering is disabled for all proxied responses at this stage.
- The supplied pytest run verifies the existing regression suite; the manual HTTP checks verify the Nginx ingress. Header spoofing/trusted forwarding, oversized-body rejection, progressive SSE delivery, and recovery after upstream address changes were not exercised by this evidence.
- Compose source assertions do not exercise Compose's merge engine. No production override or database exists yet, so production/database exposure remains future verification work. TLS and production hardening remain Phase 12 work.
- P01-T03 remains **Not started**. It is the immediate next lesson; do not advance to P01-I04 before its required tests pass. Tests must continue to prepare their inputs automatically and run with plain `pytest` inside the normally started API container.

## P01-T03 · Nginx proxy and network isolation

**In progress — first increment verified 2026-11-16.** Reviewed the new, untracked [test_nginx.py](../../src/chathat/core/tests/test_nginx.py). No blocking issues found in this increment. The test sends a real HTTP request to `http://nginx/health` from the API container, exercising Nginx → Uvicorn rather than API-container loopback. `ProxyHandler({})` disables environment-configured HTTP proxies, the request has a five-second timeout, and the response context manager closes the connection. Assertions verify HTTP 200, the JSON content type, and the exact `{"status": "ok"}` payload. No persistent test state or special test configuration is introduced.

### Supplied verification evidence

The user supplied output for `docker compose -f compose.yaml -f compose.dev.yaml exec api pytest`: **9 passed in 1.33s**, on Linux with Python 3.12.7 and pytest 9.2.0. Collection includes five application tests, three container tests, and the new Nginx health test. Tests were not rerun during this documentation update.

### Completion and scope decision — 2026-11-17

**Completed within the user-approved no-special-setup scope.** The user required all tests to run through `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest` and excluded tests needing special setup. The user then explicitly requested that P01-T03 be recorded as completed. This narrows the original lesson's acceptance scope; it does not establish the deferred behaviors below.

Added three tests alongside the existing Nginx health test:

- The `/health/` redirect preserves the supplied Host (including port) and uses HTTP despite spoofed `X-Forwarded-Proto`, `X-Forwarded-Host`, and `Forwarded` headers. This verifies observable host/scheme behavior, not client-IP forwarding or positive HTTPS forwarding.
- Nginx returns the expected stylesheet with a CSS content type; the direct API returns 404 for the same asset path.
- A Content-Length of 10 MiB plus one byte receives an Nginx HTTP 413 before the body is sent. This verifies early declared-size rejection, not streamed/chunked-body enforcement or the exact accepted-size boundary.

Ran `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest` and observed **12 passed in 1.22s**, on Linux with Python 3.12.7 and pytest 9.2.0: five application tests, three container tests, and four Nginx tests. No extra setup, dependencies, application routes, or test-specific environment variables were introduced.

### Deferred coverage

- Progressive SSE delivery is excluded from this lesson's completed scope because the running app has no SSE endpoint; testing it would require additional setup. The original curriculum requirement remains deferred, not verified.
- Full client-IP forwarding and positive trusted HTTPS forwarding remain unverified.
- Existing Compose source assertions cover API port non-publication and Nginx-only development publication. They do not validate Compose's merge engine or prove external runtime port isolation.
- Production-model application/database isolation remains deferred because `compose.prod.yaml` and PostgreSQL do not exist yet. Verify when the relevant infrastructure exists.

Phase progress is **8/14 (57.1%)**. The next lesson is **P01-I04 — Typed settings and environment boundaries**.

Updated `CODEBASE_MAP.json` for the four declared test functions during the preceding authorized test changes. This progress-only update does not change indexed responsibilities or declarations, so no further map edit is needed.
