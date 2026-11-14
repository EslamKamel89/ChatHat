# P01-I02 · Dockerfile and development Compose foundation

Run the existing FastAPI app inside Docker Compose with source reload, a health check, and an isolated Python environment built from `uv.lock`.

P01-T07 is complete with five passing tests and a Uvicorn health demonstration. The checkout has Python packaging and feature-local tests. This lesson adds five files at the repository root. Nginx follows in P01-I03 and PostgreSQL/pgvector in P01-I05. The temporary development endpoint here binds to host loopback. [Implementation plan](../../chathat-implementation-plan.md#p01-i02--implement-dockerfile-and-development-compose-foundation) · [Phase notes](../../progress-documentation/phase-01-notes.md#p01-t07--verify-feature-local-test-discovery-and-core-behavior)

## Contract

| Boundary        | Expected behavior                                                                                                   |
| --------------- | ------------------------------------------------------------------------------------------------------------------- |
| Image build     | Installs the project and development dependencies from the existing lockfile. An outdated lockfile fails the build. |
| Container start | Runs the installed `chathat.main:create_app` factory as a non-root user.                                            |
| Development     | Binds source into the container and reloads Uvicorn when Python source changes.                                     |
| Health          | Returns HTTP 200 with `{"status":"ok"}` and eventually reports healthy in Compose.                                  |
| Environment     | Host `.venv` and `.env` stay outside the build context.                                                             |
| Tests           | Pytest runs inside the application container and discovers the five core tests.                                     |

You need Docker Engine running and the Docker Compose plugin. Verify them before typing the files.

```sh
docker version
docker compose version
```

## 1. Limit the build context

Create `.dockerignore` at the repository root.

```text
.git
.venv
**/__pycache__
**/*.pyc
.pytest_cache
.env
.env.*
!.env.example
*.pem
*.key
secrets
uploads
storage
backups
dist
build
```

Docker sends the build context to its builder. These patterns exclude local environments, caches, and private runtime files. The Dockerfile below also copies only the files needed to install the application. Check both the ignore rules and COPY instructions when adding future build inputs.

## 2. Build the application image

Create `Dockerfile` at the repository root.

```dockerfile
FROM python:3.12.7-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:0.13.7 /uv /usr/local/bin/uv

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

RUN groupadd --gid 10001 chathat \
    && useradd --uid 10001 --gid chathat --create-home chathat \
    && chown chathat:chathat /app

COPY --chown=chathat:chathat pyproject.toml uv.lock README.md ./
COPY --chown=chathat:chathat src ./src

USER chathat

RUN uv sync --locked --group dev --no-cache

EXPOSE 8000

CMD ["uvicorn", "chathat.main:create_app", "--factory", "--lifespan", "on", "--host", "0.0.0.0", "--port", "8000"]
```

The Python and uv version tags establish the lesson's build inputs. The lockfile supplies resolved Python dependencies. Image tags can be republished, so exact image digests belong in the production image-pinning work in Phase 12.

`uv sync --locked` creates `/app/.venv` and installs the project in editable mode. It fails when the project metadata requires a lockfile update. Development dependencies include pytest and the HTTP client used by TestClient. The PATH points directly at the environment, so startup runs the installed Uvicorn without resolving dependencies again. [uv Docker integration](https://docs.astral.sh/uv/guides/integration/docker/)

The image build installs dependencies as user 10001, who owns `/app`. That same user runs the server. Exec-form CMD passes the server process directly to the container runtime, allowing it to receive the shutdown signal. `0.0.0.0` listens on container interfaces so Docker can forward traffic to it. `EXPOSE` documents the port.

## 3. Define the shared service

Create `compose.yaml`.

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Dockerfile
    init: true
    networks:
      - backend
    healthcheck:
      test:
        - CMD
        - python
        - -c
        - "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=2).close()"
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 5s

networks:
  backend:
```

The service builds from the repository root. The `backend` network connects future services through Compose DNS, where this service will be reachable as `api`. Compose prefixes resource names with its project name. Use `-p` consistently when you want a second, isolated project.

The health check runs inside the container against loopback. An unsuccessful HTTP response or connection failure exits with an error. Health status describes readiness after startup. When services later depend on each other, Compose can wait for a dependency's health condition. Runtime connection failures still need application handling.

`init: true` supplies a small init process that forwards signals and reaps child processes, including those used by the development reloader.

## 4. Add development behavior and local configuration

Create `compose.dev.yaml`.

```yaml
services:
  api:
    command:
      - uvicorn
      - chathat.main:create_app
      - --factory
      - --lifespan
      - "on"
      - --host
      - 0.0.0.0
      - --port
      - "8000"
      - --reload
      - --reload-dir
      - /app/src
    ports:
      - "127.0.0.1:${CHATHAT_DEV_PORT:-8000}:8000"
    volumes:
      - ./src:/app/src:ro
```

Create `.env.example`.

```dotenv
CHATHAT_DEV_PORT=8000
```

The later Compose file overrides the service command and adds the development port and source mount. Paths in both files resolve relative to the first Compose file. Inspect the merged result whenever you change overrides. [Compose merge rules](https://docs.docker.com/compose/how-tos/multiple-compose-files/merge/)

The bind mount exposes your host source at `/app/src`, where the editable package imports it. It overlays the image's source copy and leaves `/app/.venv` intact. The read-only mount allows the container to read host edits. Uvicorn watches that directory and restarts its application process after changes.

This mount differs from a named volume, which Docker manages independently of your checkout and which will later hold persistent database data. The container filesystem can be recreated from its image.

Compose reads `.env` for variable interpolation. Here the variable selects a host port. Application settings arrive in P01-I04. Copy the example only if a local `.env` does not already exist, then edit the port if necessary.

```sh
test -e .env || cp .env.example .env
docker compose -f compose.yaml -f compose.dev.yaml config
```

## 5. Build, start, and demonstrate

Stop any earlier host Uvicorn process using port 8000, or choose another `CHATHAT_DEV_PORT`.

```sh
docker compose -f compose.yaml -f compose.dev.yaml up --build -d --wait
docker compose -f compose.yaml -f compose.dev.yaml ps
curl -i http://127.0.0.1:8000/health
```

Use the configured host port in curl if you changed it. Expect a healthy `api` container and HTTP 200 with `{"status":"ok"}`. If startup fails, inspect logs.

```sh
docker compose -f compose.yaml -f compose.dev.yaml logs --tail=100 api
```

To demonstrate reload, add a temporary comment to `src/chathat/core/routes/health.py`, save it, and watch the logs for an application restart. Request health again, then remove the comment. The installed base Uvicorn reloader polls Python file changes.

## 6. Run tests inside the container

```sh
docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -q
```

Expect the same five core tests to pass. `exec` runs a command in the existing service container, sharing its installed dependencies and mounted source. The upcoming P01-T02 lesson adds verification of the container and Compose contracts.

Rebuild after changing `pyproject.toml` or `uv.lock`. Source edits are picked up through the mount. Stop this Compose project when finished.

```sh
docker compose -f compose.yaml -f compose.dev.yaml down
```

## Review and next lesson

You added `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.dev.yaml`, and `.env.example`. The demonstration covers build, health, source reload, and containerized pytest. All commands and outcomes in this walkthrough are proposed and await execution in your checkout.

Next is **P01-T02 — Dockerized FastAPI and Compose configuration**. After verification, record the exact commands and observed results in the phase notes and update the source map. [Phase tracker](../../progress-documentation/phase_1.md)
