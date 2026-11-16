# ChatHat

**ChatHat** is a multi-tenant SaaS platform for creating AI-powered website chatbots. Organizations can configure and publish chatbots, connect reusable knowledge bases, upload documents, and embed a chatbot on their websites. ChatHat is designed to answer visitors using the organization's own content, offer support actions when information is insufficient, and provide administrators with conversation and answer-inspection tools.

> **Project status:** Planning and implementation preparation. The repository currently contains project documentation; the application is being built incrementally.

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

The application setup and executable Docker Compose commands will be documented as the foundation lessons are implemented. Until then, start with the [implementation plan](docs/chathat-implementation-plan.md) and track work in the [Phase 01 progress document](docs/progress-documentation/phase_1.md).

## Repository

[github.com/EslamKamel89/ChatHat](https://github.com/EslamKamel89/ChatHat)
