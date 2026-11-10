# Phase 01 — Containerized Application Foundation: Progress Tracker

> **Source of truth:** [Implementation plan](../chathat-implementation-plan.md), Phase 01.  
> **Specification:** [ChatHat specification](../chathat-spec.md), section 24 (Docker Compose and Nginx).  
> **Progress:** 2 / 14 lessons completed (14.3%).\
> **Last reviewed:** 2026-11-11.

## Lesson progress

Update a row **only after** the lesson's work and verification are complete. Record the completion date as `YYYY-MM-DD` and link the relevant commit/PR or test evidence where available.

| Lesson | Type | Lesson name | Status | Date completed | Commit / evidence | Notes |
|---|---|---|---|---|---|---|
| P01-I01 | Implement | FastAPI package and application factory | Completed | 2026-11-10 | [Smoke check and implementation index](phase-01-notes.md#verification) | Verified HTTP 200 and 503, lifespan, and factory isolation. |
| P01-T01 | Test | FastAPI package and application factory | Completed | 2026-11-10 | [pytest result](phase-01-notes.md#p01-t01--test-the-fastapi-package-and-application-factory) | 5 passed in 0.26s in the user's local run. |
| P01-I07 | Implement | Organize the application foundation by feature | Not started | — | — | Introduces TECH-014 before Docker setup. |
| P01-T07 | Test | Verify feature-local test discovery and core behavior | Not started | — | — | — |
| P01-I02 | Implement | Dockerfile and development Compose foundation | Not started | — | — | — |
| P01-T02 | Test | Dockerized FastAPI and Compose configuration | Not started | — | — | — |
| P01-I03 | Implement | Nginx Compose service and internal routing | Not started | — | — | — |
| P01-T03 | Test | Nginx proxy and network isolation | Not started | — | — | — |
| P01-I04 | Implement | Typed settings and environment boundaries | Not started | — | — | — |
| P01-T04 | Test | Configuration and secret safety | Not started | — | — | — |
| P01-I05 | Implement | PostgreSQL/pgvector, SQLModel and Alembic | Not started | — | — | — |
| P01-T05 | Test | PostgreSQL persistence and migration lifecycle | Not started | — | — | — |
| P01-I06 | Implement | Containerized developer commands and CI | Not started | — | — | — |
| P01-T06 | Test | Fresh-checkout reproducibility and CI contract | Not started | — | — | — |

**Status values:** `Not started`, `In progress`, `Blocked`, `Completed`. A lesson is **Completed** only when its acceptance checks pass; a testing lesson additionally requires passing pytest results.

## Completion rules

1. Follow the listed order: each implementation lesson (`Ixx`) is immediately followed by its matching pytest lesson (`Txx`). Do not begin the next implementation lesson until the preceding test lesson passes.
2. Update the status when work starts, finishes, or becomes blocked. Record a brief blocker or outcome in **Notes**.
3. When completed, add the date and a commit/PR link or reproducible command and test result under **Commit / evidence**. Never mark lessons completed solely because they are planned.
4. Calculate progress as **completed rows / 14** and keep the summary above synchronized with the table.
5. Preserve previous outcomes or important decisions in the notes/history below if a lesson is reopened.

## Phase exit checklist

- [ ] Nginx routes requests to FastAPI through Docker Compose.
- [ ] Development FastAPI source changes reload inside its container.
- [ ] PostgreSQL/pgvector persists data and passes migrations.
- [ ] Isolated pytest runs inside containers without touching development or production databases.
- [ ] Containerized developer commands and CI checks are reproducible from a fresh checkout.
- [ ] All 14 lesson rows are marked **Completed** with verification evidence.

## Progress notes and blockers

_Add dated entries here when a decision, failure, or deviation affects Phase 01._
