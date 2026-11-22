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

- [tests/test_app.py](../../src/chathat/core/tests/application/test_app.py) covers HTTP 200 and 503 from `/health`, HTTP 404 for an unknown route, app state isolation through startup and shutdown, and startup exception propagation.
- [pyproject.toml](../../pyproject.toml) declares `pytest` and `httpx2` in the uv development group. [uv.lock](../../uv.lock) records their resolved versions.

The user's `pytest` run from the repository root collected five tests and reported **5 passed in 0.26s** on macOS with Python 3.12.7 and pytest 9.2.0.

## P01-I07 · Organize the application foundation by feature

**Completed 2026-11-14.** Reviewed the working-tree refactor and recorded the user's repository-root `pytest` output. It collected the five tests from `src/chathat/core/tests/test_app.py` and reported **5 passed in 0.20s**, using Python 3.12.7 and pytest 9.2.0 on macOS.

| File | Reviewed change |
| --- | --- |
| [core/routes/health.py](../../src/chathat/core/routes/health.py) | Moved the original health router and response schema together. |
| [core/application/lifespan.py](../../src/chathat/core/application/lifespan.py) | Extracted the existing startup and shutdown implementation. |
| [main.py](../../src/chathat/main.py) | Imports the core router and lifespan while keeping `create_app()` as the entry point. |
| [core/tests/test_app.py](../../src/chathat/core/tests/application/test_app.py) | Moved all five tests without changing their contents. The startup failure test still patches `main.lifespan`, the name resolved by the factory. |
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

**Verified 2026-11-15.** Added [test_container.py](../../src/chathat/core/tests/infrastructure/test_container.py) with three tests covering the Compose source configuration, real Uvicorn health response, and non-root Python environment with installed dependencies. PyYAML is a locked development dependency. The image includes both Compose files so the fixture reads them automatically.

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
| [core/tests/test_container.py](../../src/chathat/core/tests/infrastructure/test_container.py) | Updates the existing Compose source assertion for Nginx port publication and absence of API port publication. The runtime API-health test still addresses Uvicorn directly. |

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

**In progress — first increment verified 2026-11-16.** Reviewed the new, untracked [test_nginx.py](../../src/chathat/core/tests/infrastructure/test_nginx.py). No blocking issues found in this increment. The test sends a real HTTP request to `http://nginx/health` from the API container, exercising Nginx → Uvicorn rather than API-container loopback. `ProxyHandler({})` disables environment-configured HTTP proxies, the request has a five-second timeout, and the response context manager closes the connection. Assertions verify HTTP 200, the JSON content type, and the exact `{"status": "ok"}` payload. No persistent test state or special test configuration is introduced.

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

## P01-I04 · Typed settings and environment boundaries

**Completed 2026-11-17.** Reviewed tracked changes and untracked settings, application-state, and dependency modules. The user reported completing the lesson and all demonstration checks. No blocking implementation issues were found.

### Implementation and decisions

- `core/settings/config.py` defines `Config(BaseSettings)` with a required development/test/production environment, boolean debug setting, and optional `SecretStr` excluded from model dumps. Configuration uses the `CHATHAT_` prefix, disables dotenv loading, prevents reassignment, and hides inputs in formatted validation errors. Production rejects debug mode, missing secrets, and secrets shorter than 32 characters; length alone does not establish entropy.
- `main.create_app(*, config: Config | None = None)` resolves configuration before application startup, applies debug mode, and stores a frozen, slotted `AppState(config=resolved_config)` at `app.state.resources`.
- `core/application/state.py` owns the typed resource container and accessor. `core/dependencies/state.py` exposes `provide_app_state` and `AppStateDependency`; requests retrieve the owning application's existing configuration rather than reloading it.
- The implementation uses `Config` and an `AppState` resource container instead of the walkthrough's `Settings` class and direct settings dependency. Settings live in a responsibility subdirectory, consistent with the updated specification §2.2 and AGENTS.md directory-only feature-root rule. The settings directory currently uses namespace-package behavior without an `__init__.py`; existing imports pass in the container.
- Development Compose explicitly supplies the development environment and interpolated debug flag. `.env.example` contains only non-secret development values. `pydantic-settings` is declared and locked; the existing Dockerfile installs the locked dependencies and excludes populated environment files from the build context.
- Reviewed the existing AGENTS.md/specification layout changes without modifying them. The plan's baseline version label remains historical; the current specification is v0.4.2.

### Verification evidence and limits

Ran `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest` and observed **12 passed in 1.29s**, on Linux with Python 3.12.7 and pytest 9.2.0. These are the existing five application, three container, and four Nginx tests. The user's successful demonstration checks are reported confirmation; their console output was not supplied or independently rerun during this review.

The regression suite does not establish configuration precedence, complete production-validation boundaries, secret-safe logs/responses, or dependency-override isolation. Those are the immediate paired **P01-T04 — Configuration and secret safety** lesson, which remains not started. No authentication/signing implementation is implied by the secret field.

Updated affected navigation summaries and indexed the new modules, declared configuration/state types, dependency alias, and changed factory signature. Phase progress is **9/14 (64.3%)**.

## P01-T04 · Configuration and secret safety

**Completed 2026-11-17.** Reviewed the new, untracked `src/chathat/core/tests/test_config.py` against the implementation and lesson contract. No blocking issues found. The existing `commands.txt` change was reviewed and preserved; no application code was modified during this update.

### Coverage and isolation

- A module-local, function-scoped autouse fixture removes inherited `CHATHAT_*` values using `monkeypatch`, which restores them after each test. Temporary dotenv files and working-directory changes are prepared and cleaned up automatically by pytest. No manual configuration, extra service, dependency installation, or test-specific environment setup is required.
- Tests cover constructor/environment/default precedence, boolean parsing, disabled implicit dotenv loading, missing/invalid environment and debug values blocking factory creation, production debug/secret failures, the 31/32-character boundary, and development/test behavior without credentials.
- Secret tests check masked representations, model-dump exclusion, formatted validation-error logging, and synthetic secret absence from current health/OpenAPI/404 responses, headers, and captured request logs. They do not guarantee safety when explicitly extracting raw secrets or logging raw error dictionaries, nor coverage of future endpoints.
- Application tests verify immutable configuration, independent per-application snapshots, dependency overrides isolated to one application, restoration after clearing overrides, and unchanged stored application resources. Test-only routes exist only on fresh in-process apps; the running service is not modified.

### Supplied verification evidence

The user supplied `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v` output reporting **29 passed in 1.39s**, on Linux with Python 3.12.7 and pytest 9.2.0. The suite consists of five application tests, **17 configuration cases**, three container tests, and four Nginx tests. The lesson's earlier prediction of 30 total tests was an arithmetic error; static inspection confirms 17 new cases and 29 total, with no described test omitted. Tests were not rerun during this documentation update. `-v` only changes reporting; tests remain discoverable through the required command without additional flags or setup.

Indexed the new module's actual fixture/test signatures and decorators without inferring missing return annotations. Phase progress is **10/14 (71.4%)**. The next lesson is **P01-I05 — PostgreSQL/pgvector, SQLModel and Alembic**.


## P01-I05 · PostgreSQL/pgvector, SQLModel and Alembic

**Completed 2026-11-19.** Reviewed the working-tree diff, staged lockfile, and untracked database/migration modules against I05. The user reported successful completion and supplied the migration, query, and regression output below. No blocking implementation issues were found. Only the tracker, these notes, and the navigation index were modified during this review; staged and unrelated work was preserved.

### Implementation and decisions

- Base Compose now defines PostgreSQL/pgvector (`pgvector/pgvector:pg16`), its `postgres_data` named volume, initialization configuration, health check, and an API dependency on database health. Development Compose adds the masked application URL and a separate `test-db` server with its own role and `postgres_test_data` volume; API startup waits for test-server health as well. Neither database publishes a host port. These definitions prepare isolated infrastructure; guarded per-run test-database creation and cleanup are still T05 work.
- The implementation additionally includes development-only pgAdmin (`dpage/pgadmin4:9.19`), bound to loopback port 5050 with separate persistent storage and an environment-supplied password. `.env.example` contains empty password placeholders. Development startup now requires both database and pgAdmin password inputs; no manual test-specific configuration is introduced. Unlike the walkthrough, development database initialization settings live in base Compose. Production credentials and least-privilege runtime/migration roles remain deployment work.
- SQLModel metadata and deterministic constraint/index naming live directly in `core/database/__init__.py`, rather than a separate `metadata.py`. This respects directory-only feature roots. No business tables or tenant-owned data are introduced; future model imports must populate this metadata before autogeneration.
- `Database` owns an async engine and SQLModel async-session factory. Engine creation is lazy, with pre-ping, pool size five, up to five overflow connections, ten-second pool wait, five-second connection timeout, hidden SQL parameters, and `expire_on_commit=False`. Pool limits apply per application process. `AppState` holds an optional database; the factory creates it only when a database URL exists, and lifespan awaits engine disposal at shutdown.
- Configuration validates an optional `SecretStr` URL for the PostgreSQL asyncpg driver, host, and database, excluding it from dumps. Existing health/configuration-only application behavior remains possible without a database. `/health` still reflects application startup rather than database/schema readiness.
- `provide_session` yields a request-owned session, closes it on dependency exit, and returns HTTP 503 when database resources are absent. Commit boundaries remain explicit in business operations; closing unfinished sessions rolls back their transactions. Session ownership is not tenant authorization.
- The Alembic environment uses shared metadata, validated runtime or programmatic URLs, optional supplied synchronous connections, and an async engine with `NullPool`. `run_sync` bridges migration operations; the environment disposes its engine. Generated Alembic configuration retains console logging, explaining the INFO messages in the supplied output. The revision template includes SQLModel type support.
- Revision `0001_pgvector` lives in `migrations/versions/0001_pgvector_enable_pgvector.py`. Upgrade creates the vector extension; downgrade drops it without `CASCADE`. Startup does not migrate or call `create_all()`. The Dockerfile packages configuration and migrations; changes to these image-baked files require rebuilding. Runtime dependencies and the staged lockfile include SQLModel, SQLAlchemy asyncio, asyncpg, and Alembic.
- `commands.txt` adds revision-generation and upgrade commands. Its revision-generation example is specific to creating the initial revision and should not be rerun unchanged for later migrations. A newly added comment has trailing whitespace (`commands.txt:10`); this nonblocking formatting issue was reported and left unchanged. The README's documentation-only project-status statement remains stale and outside this update's scope.

### Supplied verification evidence and limits

The user supplied these results, all using the development Compose files and the API container:

- `python -m alembic history`: `<base> -> 0001_pgvector (head), Enable pgvector.`
- `python -m alembic upgrade head`: PostgreSQL transactional DDL and successful upgrade from base to `0001_pgvector`.
- `python -m alembic current`: `0001_pgvector (head)`.
- Async SQLModel session demonstration: `database=chathat; vector=0.8.7; distance=0.0`, confirming the development database identity, enabled extension, and real vector-distance operation.
- `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest`: **29 passed in 2.17s**, Linux, Python 3.12.7, pytest 9.2.0. These are the unchanged five application, 17 configuration, three container, and four Nginx cases.

These are user-supplied results, not commands rerun by the assistant during this update. They establish I05's migration/query smoke behavior and existing regression compatibility. They do not establish automated database constraints, transaction rollback, session cleanup, guarded test teardown, or migration downgrade behavior. No restart output was supplied; persistence after container restart remains unverified, so the combined phase persistence checklist remains unchecked.

The immediate next lesson is **P01-T05 — PostgreSQL persistence and migration lifecycle**. Its fixtures must automatically use isolated databases on `test-db` under the unchanged standard pytest command, with explicit protections against development/production targets. Automated container-restart control remains to be resolved there; a reconnect check is not proof of persistence after a container restart. T05 is not started and no dedicated database tests are claimed complete.

Updated the navigation index for changed responsibilities and actual new declarations, including the package-level metadata export and generated revision paths. Phase progress is **11/14 (78.6%)**.


## P01-T05 · PostgreSQL persistence and migration lifecycle

**Initial review 2026-11-22; completion was pending at this point (resolved below).** Reviewed both untracked test modules, current infrastructure and migration/session wiring, and the user-supplied pytest results. The implemented cases have no blocking correctness issues identified in this review. The mandatory container-restart persistence criterion is not covered; the lesson remains **In progress**, without a completion date or approved deferral. Phase progress remains **11/14 (78.6%)**. The unrelated skill-file edit and all implementation/test files were preserved.

### Isolation, coverage, and decisions

- `core/tests/database_support.py` fixes administration to `test-db:5432`, the dedicated test role, and its public disposable-fixture credential. It does not read the development URL. Target validation requires the expected driver, host, port, username/password, no query overrides, and a generated `chathat_test_<32 hex>` database name.
- Each function-scoped database fixture creates a database from `template0`. Cleanup runs after successful creation even when the context body fails; it validates the target and database owner, drops only the generated test database, and checks catalog removal. Administration and target connections close in finally blocks. Application engines are disposed within the same async scenario/event loop that uses them.
- Seven guard cases reject unsafe targets; two cleanup cases verify removal after successful and failing contexts. A migration test checks clean upgrade, repeated upgrade, actual vector-distance operation, downgrade, and reupgrade. Another verifies that a synthetic table is absent from a second generated database.
- Four PostgreSQL constraint cases cover primary-key/unique, not-null, and check violations by SQLSTATE, then prove the session can query after transaction rollback. The synthetic `probe` table is test-owned; this does not establish future product-model constraints or tenant authorization.
- Further tests cover explicit transaction rollback, rollback on unfinished session close, committed rows through a replacement engine, successful/failing/unfinished test-only API requests, a real pooled-connection close event after application lifespan exit, and HTTP 503 without database resources. The close event proves closure occurred, not an exhaustive inventory of all possible connection leaks.
- No extra service, dependency, environment variable, manual database preparation, skip, or alternate command was introduced. Tests use the already-started development `test-db` service and the existing read-only `src` mount. The phase's isolated-pytest exit criterion is now checked from the supplied run and source-reviewed fixture isolation.

### User-supplied evidence

`docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v` reported **47 passed, 25 warnings in 3.20s**, on Linux, Python 3.12.7, pytest 9.2.0, with anyio 4.16.0. This comprises **18 new database cases** and the **29 existing regression cases**, with no skips. The result matches the reviewed test names and parametrization. The assistant did not rerun pytest, migrations, or database cleanup during this review.

The warnings are non-failing deprecations: **11** from Alembic's missing `path_separator` setting and **14** from SQLModel's `session.execute()` wrapper. They are retained as maintenance findings; neither Alembic configuration nor test calls were changed as part of verification. The helper's declared context-manager return annotations are `AsyncGenerator[...]`; the index records those actual annotations rather than the walkthrough's `AsyncIterator[...]`.

### Initial outstanding acceptance criterion (resolved below)

At the initial review, the suite did not restarts a PostgreSQL container. `test_rollback_close_and_committed_reconnection` disposes one engine and opens another while the same database server remains running; that is not evidence of persistence after a container restart. At that point the API service had no container-restart control, and the user requires all tests to run through the existing command without special setup. The prior walkthrough disclosed this gap, but disclosure alone is not an approved deferral.

At that review, the verification skill and lesson contract required leaving completion unrecorded until restart coverage was verified or the user approved a scope deferral. The combined phase database-persistence checklist was left unchecked and P01-I06 was not started.

Indexed both new modules' actual top-level helpers, fixtures, tests, annotations, keyword-only defaults, async metadata, and decorators. Sensitive connection values, SQL bodies, nested local helpers, and verification results are excluded from the navigation index.


### Restart coverage implemented and verified — 2026-11-22

**P01-T05 completed; no acceptance deferral.** The user explicitly authorized implementing the missing coverage directly, with all tests still triggered only through `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v`.

- Development `test-db` now has `restart: always` and a fixed `cluster_name=chathat_test_restartable` marker. No additional service, Docker socket mount, package, external controller, or user-supplied test setting was added. Development `db` is unchanged.
- The guarded restart helper accepts only the existing allowlisted generated test URL, checks the marker, and requires PostgreSQL to be PID 1. It reads Linux `/proc/1/stat` start ticks (with an explicit length for procfs) and PostgreSQL startup time before sending the fixed `kill -INT 1` command through PostgreSQL's privileged server-program facility. SIGINT performs orderly fast shutdown; Docker restarts the exited test container. The existing dedicated test administration role has the required privileges; this helper is not application or production code.
- The helper allows Docker's ten-second successful-start window, handles the expected shutdown disconnection, and polls readiness with a bounded timeout. It requires both a changed PID 1 process start identity and a later PostgreSQL startup timestamp. A stale Compose configuration fails at the marker check before shutdown rather than silently stopping an unconfigured server.
- The new test commits a synthetic row, disposes its original engine, restarts the isolated test container, then verifies exact row values, retained Alembic revision `0001_pgvector`, and a real pgvector distance operation through new application database resources. Ordinary fixture teardown then removes its generated database. This covers a graceful container restart, not abrupt power loss, backup restoration, or volume replacement. Run the standard serial suite once per stack; restarting the shared test server can interrupt concurrent independent database suites.

Assistant-run preparation used the normal development startup command `docker compose -f compose.yaml -f compose.dev.yaml up --build -d --wait` to apply the Compose change and refresh image-baked configuration. It succeeded; no volumes were removed and no development migrations were run. This is normal stack startup, not an alternate test trigger.

Assistant-run verification used exactly:

```sh
docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v
```

**Observed: 48 passed, 28 warnings in 3.68s**, Linux, Python 3.12.7, pytest 9.2.0. All **19 database cases** and **29 regression cases** passed, including the new restart case, with no skips. The non-failing deprecations remain: 12 Alembic path-separator warnings and 16 SQLModel execute-wrapper warnings. No unrelated warning cleanup was performed.

A supplementary read-only Docker inspection of the observed test container reported `restart_count=1 status=running policy=always`, independently confirming that Docker actually restarted it. This inspection did not trigger tests. Existing user-supplied 47-pass evidence above is preserved as the pre-change baseline.

Updated the affected Compose/helper/test index entries and validated declarations and paths. The tracker now records **12/14 (85.7%)**, checks database migration/persistence, and names **P01-I06 — Containerized developer commands and CI** as the immediate next lesson. No commits, pushes, or unrelated skill edits were made.


### Test-directory decision and verified refactor — 2026-11-22

The user approved grouping tests by responsibility inside every feature's existing `tests/` directory. This is the rule for future features as well as core: mirror the feature's responsibility subpackages, create groups only when needed, include `__init__.py` markers, keep helpers with their responsibility, and place shared fixtures in the nearest applicable `conftest.py`. A feature-wide `tests/conftest.py` is permitted; test modules must not accumulate at the `tests/` root. Keep autouse fixtures scoped to the tests that need them. Infrastructure spanning external configuration uses `core/tests/infrastructure/`.

Applied moves:

| Previous location under `core/tests/` | Current location under `core/tests/` |
| --- | --- |
| `test_app.py` | `application/test_app.py` |
| `test_config.py` | `settings/test_config.py` |
| `database_support.py` | `database/support.py` |
| `test_database.py` | `database/test_database.py` |
| `test_container.py` | `infrastructure/test_container.py` |
| `test_nginx.py` | `infrastructure/test_nginx.py` |

Added package markers for all four groups and changed the database helper import to `chathat.core.tests.database.support`. Test logic and fixture scope were preserved. `CODEBASE_MAP.json` was reconciled for the moved paths/namespaces and new markers; 42 entries were validated. Earlier evidence retains its historical path text; clickable links now point to the current files.

Assistant-run post-refactor verification used exactly `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v` and observed **48 passed, 28 existing warnings in 3.93s**. All nested tests were discovered, including actual container-restart persistence coverage. Index and staged/unstaged whitespace checks passed. No extra test trigger, dependency, service, environment variable, or manual test preparation was introduced by the directory refactor.

The rule is now documented in `AGENTS.md`, specification §2.2 (v0.4.3), the implementation plan, and the lesson delivery guide. This documentation update does not change code or invalidate the preceding test evidence; pytest was not rerun for prose-only changes. T05 remains completed, phase progress remains **12/14 (85.7%)**, and the next lesson remains **P01-I06**.
