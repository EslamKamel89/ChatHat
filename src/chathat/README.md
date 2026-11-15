# ChatHat source map

Last completed lesson **P01-I03 — Nginx Compose service and internal routing**. [Progress tracker](../../docs/progress-documentation/phase_1.md) · [Phase 01 notes](../../docs/progress-documentation/phase-01-notes.md)

| File | Read it for |
| --- | --- |
| [`src/chathat/main.py`](main.py) | `create_app()` assembles the app from core. The installed Uvicorn entry point is `chathat.main:create_app`. |
| [`core/routes/health.py`](core/routes/health.py) | Health router. Returns HTTP 200 after startup and HTTP 503 when the startup flag is absent or false. |
| [`core/schemas/health.py`](core/schemas/health.py) | `HealthResponse` defines the successful health response schema. |
| [`core/application/lifespan.py`](core/application/lifespan.py) | Sets and clears `app.state.started`. [Application setup notes](core/application/README.md) |
| [`src/chathat/__init__.py`](__init__.py), [`core/__init__.py`](core/__init__.py), [`core/tests/__init__.py`](core/tests/__init__.py) | Package markers. |
| [`core/tests/test_app.py`](core/tests/test_app.py) | Five in-process API tests for health and routing, app state isolation, lifespan, and startup failure. |
| [`core/tests/test_container.py`](core/tests/test_container.py) | Three checks for Compose source configuration (Nginx-only development port publication), running Uvicorn health, and the non-root Python environment. Run `pytest` inside the active API container. |
| [`pyproject.toml`](../../pyproject.toml), [`uv.lock`](../../uv.lock) | Python 3.12+, the `uv_build` backend, runtime dependencies, and the `pytest`, `httpx2`, and PyYAML development dependencies. |
| [`dockerfiles/Dockerfile.api`](../../dockerfiles/Dockerfile.api) | Builds the API image with locked dependencies and runs the factory as a non-root user, trusting proxy headers only from Nginx at `172.30.0.10`. |
| [`compose.yaml`](../../compose.yaml), [`compose.dev.yaml`](../../compose.dev.yaml) | API/Nginx services and health checks, default network subnet and fixed proxy address, development source mount/reload, and Nginx-only loopback port publication. |
| [`nginx/default.conf`](../../nginx/default.conf), [`nginx/static/site.css`](../../nginx/static/site.css) | DNS-resolved API proxy, forwarding headers, body limits, streaming settings, and public static delivery. [Decisions and verification](../../docs/progress-documentation/phase-01-notes.md#p01-i03--nginx-compose-service-and-internal-routing) |
| [`.dockerignore`](../../.dockerignore), [`.env.example`](../../.env.example), [`commands.txt`](../../commands.txt) | Build exclusions, host-port example, and development Compose commands. |

Next lesson **P01-T03 — Nginx proxy and network isolation**. [Implementation plan](../../docs/chathat-implementation-plan.md#p01-t03--test-nginx-proxy-and-network-isolation)
