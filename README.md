# ChatHat

**ChatHat** is a multi-tenant SaaS platform for creating AI-powered website chatbots. Organizations can configure and publish chatbots, connect reusable knowledge bases, upload documents, and embed a chatbot on their websites. ChatHat is designed to answer visitors using the organization's own content, offer support actions when information is insufficient, and provide administrators with conversation and answer-inspection tools.

> **Project status:** The containerized FastAPI foundation includes Nginx, PostgreSQL/pgvector, Alembic, and container-based tests. See the Phase 01 tracker for lesson progress.

## Planned technology stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, SQLModel, Alembic |
| Database and retrieval | PostgreSQL, pgvector, PostgreSQL full-text search |
| AI orchestration and memory | LangGraph, checkpointed conversations |
| Background processing | Celery, Redis |
| Dashboard | Jinja2, HTMX, Alpine.js, Tailwind CSS, daisyUI |
| Website integration | Embeddable JavaScript loader and isolated iframe widget, SSE streaming |
| Infrastructure | Docker Compose (development and production), Nginx reverse proxy |
| Testing | pytest |

## Documentation

| Document | Purpose |
| --- | --- |
| [Repository navigation index](CODEBASE_MAP.json) | File responsibilities and declared symbols. Search relevant entries, then inspect source; maintenance rules are in `AGENTS.md`. |
| [Product specification](docs/chathat-spec.md) | Product requirements, architecture constraints, confirmed decisions, and acceptance criteria. **Primary reference for what ChatHat must do.** |
| [Implementation plan](docs/chathat-implementation-plan.md) | Phased, lesson-by-lesson development curriculum. Each implementation lesson is immediately followed by a pytest lesson. |
| [Phase 01 progress tracker](docs/progress-documentation/phase_1.md) | Lesson status, completion dates, evidence, notes, and phase exit criteria. |

## Development approach

ChatHat is implemented as a **project-based learning curriculum**. Each lesson builds a small, production-oriented increment, explains its design and runtime behavior, and is followed by a dedicated testing lesson. Development and testing use Docker Compose, with Nginx as the HTTP entry point. The project specification defines expected behavior; the implementation plan defines the build order; progress documents record completed work.

## Getting started

Install Docker with Compose V2. On a fresh checkout, copy `.env.example` to `.env`
and set `CHATHAT_DB_PASSWORD` and `CHATHAT_PGADMIN_PASSWORD`. Use a URL-safe
database password. Keep `.env` local.

```sh
docker compose -f compose.yaml -f compose.dev.yaml up --build -d --wait
curl --fail --silent --show-error http://127.0.0.1:8000/health
```

Nginx returns `{"status":"ok"}`. If you set `CHATHAT_DEV_PORT`, use that port.
Python source changes reload the API. Rebuild after changing dependencies,
migrations, or image-baked configuration.

Apply and inspect migrations on the local development database:

```sh
docker compose -f compose.yaml -f compose.dev.yaml exec api python -m alembic upgrade head
docker compose -f compose.yaml -f compose.dev.yaml exec api python -m alembic current
```

Run static checks and pytest inside the API container:

```sh
docker compose -f compose.yaml -f compose.dev.yaml exec api ruff check src migrations
docker compose -f compose.yaml -f compose.dev.yaml exec api mypy
docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v
```

Pytest prepares isolated databases on `test-db` automatically. Run one suite
at a time per stack because the persistence test restarts that service.

Inspect or stop the stack:

```sh
docker compose -f compose.yaml -f compose.dev.yaml ps
docker compose -f compose.yaml -f compose.dev.yaml logs --tail=100 api nginx db test-db
docker compose -f compose.yaml -f compose.dev.yaml stop
```

`stop` preserves containers and database volumes. Start the stack again with `up`.

## Repository

[github.com/EslamKamel89/ChatHat](https://github.com/EslamKamel89/ChatHat)
