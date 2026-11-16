# ChatHat — Implementation Curriculum and Phase Plan

> **Status:** Proposed implementation curriculum; implementation progress is tracked separately.  
> **Baseline** `docs/chathat-spec.md` v0.4.1, including TECH-014, Q001–Q061, and INFRA-001–INFRA-006.\
> **Repository:** https://github.com/EslamKamel89/ChatHat  
> **Created:** 2026-11-08  
> **Repository inspection:** On 2026-11-08, the repository contained documentation including `docs/chathat-spec.md` and `docs/chathat-implementation-plan.md`; no application code was present in the inspected tree.

## Teaching contract

Each feature is delivered as a strict **implementation lesson immediately followed by a pytest lesson**. Do not start another implementation lesson until its paired tests pass. The instructor teaches by incrementally typing production-quality code and explaining *why* each significant construct exists, what executes at runtime, how data moves, failure behavior, and trade-offs. Avoid unexplained code dumps and elementary Python/FastAPI introductions.

Each **implementation lesson** must include: purpose and prerequisite contracts; precise files to create/edit; incremental code chunks; explanations of imports, annotations, dependencies, async boundaries, transactions and lifecycle where relevant; one runnable demonstration; design alternatives; and a short change summary. Show complete final code only when necessary to make the increment runnable. Never silently modify files or infer repository state: inspect the current checkout's relevant source, tests, and documentation before each lesson. The current codebase and observed test results are the single source of truth for implementation state; the specification controls requirements and this plan controls lesson order. Do not require GitHub inspection to establish implementation state.

Each **testing lesson** must include: the contract from the previous lesson; pytest fixture design; unit vs integration test rationale; happy path, important negative paths, permissions and boundary cases; executable tests; exact commands and expected results; and an explanation of what each assertion proves. Use real PostgreSQL/pgvector, Redis and Celery for relevant integration tests rather than substituting mocks for critical boundaries. Use mocks/fakes only at genuine external ports (LLM, OAuth, payment providers, object storage where appropriate). Tests must be deterministic, independent and safe to rerun.

**Naming:** `Pxx-Iyy` = implementation; `Pxx-Tyy` = its immediately following test lesson. A phase is complete only after all paired tests pass, migrations work from a clean database, and the phase's end-to-end increment is demonstrable.

**Container execution contract:** All development and production services run under Docker Compose. Nginx is a separate Compose service and the only public HTTP entry point; FastAPI runs behind it. Introduce the Dockerfile, base/dev Compose files, Nginx and PostgreSQL/pgvector in Phase 01. Add Redis/Celery when needed in Phase 05, and Celery Beat when scheduled jobs first require it. Tests and Alembic run in containers; production uses a Compose override, TLS, persistent data, backups, and hardened network exposure.

**Non-negotiable architecture:** Shared PostgreSQL tables with strict tenant isolation (Q056); canonical document embeddings across KBs (Q057); complete original messages in authoritative LangGraph checkpoint state with derived context and transcripts (Q058/Q061); monthly AI credits with atomic reservations and measured settlement (Q059); manual plan provisioning before paid launch, payment integration before charging customers (Q060). Keep separate trace/evidence snapshots as required by the spec, without creating a second authoritative conversation transcript.

**Feature packages (TECH-014)** — Use plural responsibility subpackages such as `routes/`, `schemas/`, `models/`, `services/`, and `dependencies/` as they are needed. Keep routes, schemas, models, services, dependencies, and other feature-specific code under `src/chathat/<feature>/`. Keep feature tests and fixtures in that package's `tests/` directory. The factory in `src/chathat/main.py` assembles the app and registers feature routers. [Specification §2.2](chathat-spec.md#22-feature-packages)

**Application setup** — Use `src/chathat/core/application/` for components that configure and manage the FastAPI application instance. Keep startup and shutdown in `core/application/lifespan.py`; add middleware registration, exception-handler registration, and other instance configuration modules here as needed. The factory in `src/chathat/main.py` connects these components. Feature routes, schemas, models, services, and tests remain in their respective feature directories. See the [application setup README](../src/chathat/core/application/README.md).

**Scope gates, not extra questionnaires:** Before implementing provider-specific integrations, select a compatible provider and validate contracts. Before production release, resolve payment eligibility, data protection, retention, operational budgets and measurable release thresholds. These do not block planning or the early phases.

## Curriculum map

| Phase | Focus | Implementation lessons | Pytest lessons | Total |
|---|---|---:|---:|---:|
| 01 — Containerized application foundation | Organize FastAPI by feature and run it inside Docker Compose with Nginx, typed settings, PostgreSQL/pgvector, Alembic and pytest/CI. | 7 | 7 | 14 |
| 02 — Organizations, identity and authorization | Establish shared-table multi-tenancy and secure organization-level access before introducing tenant-owned features. | 5 | 5 | 10 |
| 03 — Plans, entitlements and credit ledger | Make usage and cost enforcement part of the platform before invoking chargeable models; use manually provisioned plans. | 3 | 3 | 6 |
| 04 — Chatbot configuration and knowledge-base relationships | Build the tenant-facing chatbot lifecycle and document/knowledge-base associations before ingestion. | 4 | 4 | 8 |
| 05 — Document library and asynchronous ingestion | Implement canonical organization-owned documents, safe parsing, ingestion, shared embeddings and publication. | 6 | 6 | 12 |
| 06 — Retrieval and grounded RAG answers | Implement secure hybrid search, evidence selection and model orchestration with predictable fallback behavior. | 5 | 5 | 10 |
| 07 — Checkpoint-authoritative conversations and memory | Implement Q058/Q061: LangGraph checkpoints hold complete original messages; summaries and context windows are derived. | 5 | 5 | 10 |
| 08 — Streaming website widget and domain security | Deliver the installable cross-origin iframe widget, browser lifecycle, SSE transport and support actions. | 5 | 5 | 10 |
| 09 — Answer inspection, operations and privacy | Make retrieval evidence, model behavior and tenant activity observable without exposing secrets. | 3 | 3 | 6 |
| 10 — Internationalization and customer-ready dashboard | Complete localized management journeys and the full chatbot customization experience. | 3 | 3 | 6 |
| 11 — Payments and subscription lifecycle | Integrate a verified international payment provider only after onboarding/legal feasibility is resolved. | 3 | 3 | 6 |
| 12 — Production Compose, operations and release | Harden Nginx/TLS, Compose deployments, backups, performance and security before launch. | 5 | 5 | 10 |
| **Total** | | **54** | **54** | **108** |

## Phase 01 — Containerized application foundation

**Focus:** Establish the same Docker Compose service architecture for local development and production from the beginning. Every implementation is followed immediately by its pytest verification. Nginx is a required service, not a deployment-only afterthought.

**Exit deliverable:** `docker compose -f compose.yaml -f compose.dev.yaml up --build` starts Nginx → FastAPI and PostgreSQL/pgvector; migrations and pytest run inside containers, with no host-installed application dependencies.

### P01-I01 — Implement: FastAPI package and application factory

Create `pyproject.toml`, `src/chathat/`, a FastAPI application factory, typed routers, lifespan, and `/health`. Explain app initialization versus request lifecycle, dependency boundaries, and why the app factory enables isolated tests. The initial code is runnable without external infrastructure.

### P01-T01 — Test: FastAPI package and application factory

Use pytest with `TestClient` or `httpx.AsyncClient`/`ASGITransport` and an explicit lifespan manager as appropriate. Verify routing, lifespan initialization/shutdown, health response and startup errors.

### P01-I07 — Implement: Organize the application foundation by feature

This pair runs after P01-T01 and before P01-I02. It uses new IDs so the original lesson references stay valid.

Move the health router to `src/chathat/core/routes/health.py` and its response schema to `src/chathat/core/schemas/health.py`, lifespan to `src/chathat/core/application/lifespan.py`, and the existing app tests to `src/chathat/core/tests/test_app.py`. Use `core/application/` for application-instance setup as described in its [README](../src/chathat/core/application/README.md), with `main.py` wiring those components into the factory. Adjust imports and remove the empty top-level API package after its health module moves. Keep `chathat.main:create_app` as the installed entry point and preserve the health and lifespan contracts. Update affected entries in [`CODEBASE_MAP.json`](../CODEBASE_MAP.json) within the authorized refactor scope; keep lesson status and verification evidence in the progress documents.

### P01-T07 — Test: Verify feature-local test discovery and core behavior

From the repository root, run `uv run --locked pytest -q src/chathat/core/tests` and `uv run --locked pytest -q`. Both runs must discover and pass the same five existing tests. Verify HTTP 200 and 503 from `/health`, 404 for an unknown route, lifespan cleanup and app isolation, and startup failure propagation. Keep the failure injection at the lifespan name the factory actually resolves. Check the installed factory entry point and proceed to P01-I02 after verification.

### P01-I02 — Implement: Dockerfile and development Compose foundation

Create a reproducible `Dockerfile`, `.dockerignore`, `compose.yaml`, `compose.dev.yaml`, and `.env.example`. Containerize FastAPI with bind-mounted source and Uvicorn reload in development; use named networks, dependency/health semantics, and non-root image execution where practical. Explain image build versus container start, build context, bind mounts versus volumes, Compose project isolation, and `docker compose -f compose.yaml -f compose.dev.yaml` precedence. Avoid adding Redis/Celery before the relevant phase.

### P01-T02 — Test: Dockerized FastAPI and Compose configuration

Run pytest inside the FastAPI container; add pytest-driven subprocess/HTTP smoke checks that validate the Compose-rendered config and FastAPI health through its development interface. Verify rebuild/restart behavior, dependency installation, environment separation, and that the test command is reproducible from a fresh checkout. Use `docker compose config` as a supplementary validation, not a substitute for tests.

Verify that the container's pytest command discovers the feature-local core suite from the repository root inside the container.

### P01-I03 — Implement: Nginx Compose service and internal routing

Add Nginx to base/dev Compose with version-controlled `nginx/` configuration. Route public HTTP requests to FastAPI using Compose service DNS, serve appropriate static assets, set forwarded headers, and keep FastAPI's port internal by default. Explain `proxy_pass`, trusted proxy boundaries, upstream health, request-body limits and why SSE endpoints need `proxy_buffering off` and suitable timeouts. In development, Nginx may use HTTP; production TLS comes in Phase 12.

### P01-T03 — Test: Nginx proxy and network isolation

Use pytest HTTP integration tests against the **Nginx endpoint**, not merely the FastAPI container. Check health routing, forwarded host/protocol handling under trusted proxy configuration, static response routing, oversized upload rejection and an SSE fixture that proves events arrive progressively without buffering. Verify that application and database ports are not published externally in the production Compose model.

### P01-I04 — Implement: Typed settings and environment boundaries

Use `pydantic-settings` in `src/chathat/core/` for explicit development/test/production settings, environment overrides, secret redaction and dependency injection. Keep `.env.example` safe, actual credentials out of Git and secrets out of container images. Explain configuration loading and process startup versus per-request dependencies.

### P01-T04 — Test: Configuration and secret safety

Test settings precedence, invalid/missing production settings, secret masking, dependency override isolation and that no secret values appear in generated client-facing configuration or logs. Run tests through Compose.

### P01-I05 — Implement: PostgreSQL/pgvector, SQLModel and Alembic

Add PostgreSQL with pgvector to Compose using a persistent named volume and health checks. Create async engine/session ownership, SQLModel metadata, Alembic environment and first migration. Explain startup ordering versus readiness, database transactions, migration ownership, connection pooling and why pgvector integration tests require real PostgreSQL. Define a separate isolated test database/Compose project; never run tests against production or ordinary development data.

### P01-T05 — Test: PostgreSQL persistence and migration lifecycle

Use pytest integration fixtures against isolated PostgreSQL/pgvector. Verify extension availability, migration upgrade, constraints, rollback, session cleanup, data persistence after container restart and safe test teardown. Include explicit checks that tests cannot target the development/production database accidentally.

### P01-I06 — Implement: Containerized developer commands and CI

Define documented Compose commands for start/stop/logs, running Alembic and pytest, lint/type checks and a reproducible GitHub Actions pipeline. Prefer a dedicated test Compose override or profile that isolates test infrastructure. Explain one-off `docker compose run --rm` versus `exec`, exit-code propagation, deterministic dependencies, service health and CI artifact collection.

### P01-T06 — Test: Fresh-checkout reproducibility and CI contract

Execute the pytest suite inside the application image, run the migration smoke test from an empty test volume, verify the Nginx entry point and inspect CI failures. Test configuration validation and test-database isolation, then document exact passing commands and expected output.

**Phase 01 demonstration:** A new developer can start the system through Nginx, edit Python code and observe reload, run migrations, run pytest and inspect logs without installing Python/PostgreSQL/Nginx on the host.

## Phase 02 — Organizations, identity and authorization

**Focus:** Establish shared-table multi-tenancy and secure organization-level access before introducing tenant-owned features.

Keep authentication routes, identity dependencies, session and sign-in logic, auth-owned models, and tests together under `src/chathat/auth/`. Keep organization membership and role policy with the organization feature.

**Exit deliverable:** A tenant-safe authenticated dashboard.

### P02-I01 — Implement: Organization and account data model

Create organizations, users, memberships/invitations consistent with one organization per user, tenant keys, indexes and invariants.

### P02-T01 — Test: Organization and account data model

Test uniqueness, foreign keys, one-org membership and cross-tenant persistence constraints.

### P02-I02 — Implement: Email/password authentication

Implement password hashing, login/logout, secure cookie session, CSRF protection, identity dependency and account flows.

### P02-T02 — Test: Email/password authentication

Test authentication, invalid credentials, cookie flags, CSRF, session expiry and unauthorized access.

### P02-I03 — Implement: Google OAuth and account linking

Integrate OAuth state/nonce validation, verified identity matching, linking policy and organization assignment.

### P02-T03 — Test: Google OAuth and account linking

Test OAuth callback with stubbed identity provider, state mismatch, account collisions and replay.

### P02-I04 — Implement: Custom RBAC and tenant-scoped policies

Implement owner-defined roles, permission assignment, permission dependencies and tenant-safe query helpers.

### P02-T04 — Test: Custom RBAC and tenant-scoped policies

Test permission matrix, privilege escalation, forged organization IDs and cross-tenant access.

### P02-I05 — Implement: Invitation and dashboard shell

Implement owner/member invitations, Jinja2 base layout, HTMX fragments, Alpine.js interactions, Tailwind/daisyUI setup.

### P02-T05 — Test: Invitation and dashboard shell

Test invitation lifecycle, permission-gated views, HTML responses and CSRF on HTMX mutations.

## Phase 03 — Plans, entitlements and credit ledger

**Focus:** Make usage and cost enforcement part of the platform before invoking chargeable models; use manually provisioned plans.

**Exit deliverable:** An auditable, concurrency-safe credit/entitlement core.

### P03-I01 — Implement: Plan catalog and manual provisioning

Model plan entitlements, usage ceilings, monthly credit grants and audited admin provisioning independent of payment APIs.

### P03-T01 — Test: Plan catalog and manual provisioning

Test entitlement checks, manual grants, authorization, audit records and downgrade blocking.

### P03-I02 — Implement: Credit ledger and reservation state machine

Implement append-only credit movements, available/reserved/consumed accounting, atomic reservations and idempotency keys.

### P03-T02 — Test: Credit ledger and reservation state machine

Test concurrent reservations, insufficient funds, duplicate operations and invariants against PostgreSQL.

### P03-I03 — Implement: Credit settlement and period lifecycle

Settle measured usage, release unused reservations, handle adjustments, period resets and recovery of stale reservations.

### P03-T03 — Test: Credit settlement and period lifecycle

Test exact settlement, failed calls, retries, rollover policy placeholders and crash-recovery paths.

## Phase 04 — Chatbot configuration and knowledge-base relationships

**Focus:** Build the tenant-facing chatbot lifecycle and document/knowledge-base associations before ingestion.

**Exit deliverable:** A manageable, publishable chatbot configuration.

### P04-I01 — Implement: Industry templates and chatbot entities

Model industry templates, chatbots, branding, rules, languages and managed retrieval strategy selection.

### P04-T01 — Test: Industry templates and chatbot entities

Test template cloning, tenant ownership, validation and immutability of platform-controlled policies.

### P04-I02 — Implement: Draft/publish and configuration versions

Implement editable drafts, immutable published revisions and effective configuration resolution for each new message.

### P04-T02 — Test: Draft/publish and configuration versions

Test publication transitions, version immutability, old conversation/new-message semantics and unauthorized publish.

### P04-I03 — Implement: Knowledge-base entities and chatbot attachments

Create reusable organization-scoped knowledge bases and chatbot↔KB associations with secure membership constraints.

### P04-T03 — Test: Knowledge-base entities and chatbot attachments

Test many-to-many membership, cross-tenant attachment denial and published bot retrieval scope.

### P04-I04 — Implement: Chatbot management dashboard

Build CRUD, template selection, branding preview, rules editing and publishing using Jinja2/HTMX.

### P04-T04 — Test: Chatbot management dashboard

Test form validation, authorization, versioned publish and server-rendered partials.

## Phase 05 — Document library and asynchronous ingestion

**Focus:** Implement canonical organization-owned documents, safe parsing, ingestion, shared embeddings and publication.

**Exit deliverable:** Reusable searchable knowledge with safe failure/retry behavior.

### P05-I01 — Implement: Object storage and secure upload pipeline

Implement S3-compatible storage adapter, file validation, SHA-256 duplicate detection, required KB selection and document records.

### P05-T01 — Test: Object storage and secure upload pipeline

Test upload types/limits, duplicates, path safety, ownership and storage failure rollback.

### P05-I02 — Implement: Celery jobs and ingestion attempt lifecycle

Create Celery integration, durable ingestion jobs/attempts, progress states, retry/idempotency and transactional publication gates.

### P05-T02 — Test: Celery jobs and ingestion attempt lifecycle

Test worker execution with real Redis/PostgreSQL integration, duplicate delivery and failed attempt recovery.

### P05-I03 — Implement: Text extraction across supported formats

Build format adapters for PDF, DOCX, TXT, MD, CSV, XLSX, HTML; handle scanned-PDF page exceptions and extraction reports.

### P05-T03 — Test: Text extraction across supported formats

Test representative fixtures, malicious/invalid files, zero-readable PDFs, partial scanned PDFs and parser failures.

### P05-I04 — Implement: Normalization, chunking and canonical embedding

Implement chunk provenance, embedding adapter, model-version keys, batch embedding and pgvector persistence without per-KB duplication.

### P05-T04 — Test: Normalization, chunking and canonical embedding

Test deterministic chunk provenance, vector dimension constraints, retries, model versioning and reuse across KBs.

### P05-I05 — Implement: Publication, detachment and global deletion

Atomically expose ready content; detach KB references; exclude deleted documents immediately and asynchronously clean vectors/files.

### P05-T05 — Test: Publication, detachment and global deletion

Test all-or-nothing publication, attachment reuse, deletion races, historical evidence retention and cleanup idempotency.

### P05-I06 — Implement: Document management and job progress UI

Build library, duplicate resolution, attach/detach, ingestion status and failure-report dashboard screens.

### P05-T06 — Test: Document management and job progress UI

Test user-visible processing states, retries, tenant authorization and HTMX updates.

## Phase 06 — Retrieval and grounded RAG answers

**Focus:** Implement secure hybrid search, evidence selection and model orchestration with predictable fallback behavior.

**Exit deliverable:** A grounded, inspectable answer engine callable internally.

### P06-I01 — Implement: Tenant-safe vector and lexical retrieval

Implement pgvector similarity, PostgreSQL full-text search, chatbot/KB filters and typed retrieval results.

### P06-T01 — Test: Tenant-safe vector and lexical retrieval

Test cross-tenant leakage, KB scope, empty results, ranking and query-plan smoke checks.

### P06-I02 — Implement: RRF fusion and contextual query rewrite

Implement Reciprocal Rank Fusion, original-query-first retrieval and conditional standalone rewrite for ambiguity.

### P06-T02 — Test: RRF fusion and contextual query rewrite

Test rank fusion determinism, rewrite triggering, fallback to original and multilingual fixtures.

### P06-I03 — Implement: Evidence sufficiency and response policy

Combine retrieval signals with model assessment; implement supported-answer and insufficient-evidence/support-action branches.

### P06-T03 — Test: Evidence sufficiency and response policy

Test supported/unsupported prompts, prompt injection in documents, evidence thresholds and support fallback.

### P06-I04 — Implement: Model gateway, retry and provider fallback

Create provider-neutral model gateway with bounded retry/backoff, compatible fallback, deadlines and measured token usage.

### P06-T04 — Test: Model gateway, retry and provider fallback

Test timeouts, provider errors, fallback sequence, usage reporting and no duplicate credit settlement.

### P06-I05 — Implement: Minimal LangGraph answer pipeline

Compose deterministic retrieval→assessment→generation steps and trace hooks without introducing long-term conversation state yet.

### P06-T05 — Test: Minimal LangGraph answer pipeline

Test graph branches with fake model/embedding ports, failure paths and provenance integrity.

## Phase 07 — Checkpoint-authoritative conversations and memory

**Focus:** Implement Q058/Q061: LangGraph checkpoints hold complete original messages; summaries and context windows are derived.

**Exit deliverable:** Durable, recoverable, tenant-safe multi-turn chat.

### P07-I01 — Implement: Conversation identity and checkpoint contract spike

Bind anonymous tab sessions to chatbot/tenant; verify supported PostgreSQL checkpointer semantics, complete-message persistence and cleanup before production schema commitment.

### P07-T01 — Test: Conversation identity and checkpoint contract spike

Integration-test restart recovery, forged thread IDs, checkpoint history, serialization cost and deletion behavior.

### P07-I02 — Implement: Original history and model-context builder

Preserve full original messages in checkpoint state; derive summary + recent N individual messages for model calls without mutating history.

### P07-T02 — Test: Original history and model-context builder

Test transcript fidelity, context window counts, system/tool exclusion, token budgets and no duplicated current request.

### P07-I03 — Implement: Synchronous incremental summary and cursor

Add summary state, cursor, compression and synchronous update before generation with explicit failure semantics.

### P07-T03 — Test: Synchronous incremental summary and cursor

Test exact-once cursor progression, summary failures, long threads and restart consistency.

### P07-I04 — Implement: Serialized turns and durable operation lifecycle

Enforce one active response per thread, operation idempotency, completion persistence and safe recovery after process failures.

### P07-T04 — Test: Serialized turns and durable operation lifecycle

Test concurrent sends, duplicate requests, checkpoint write failure, replay and transcript projection rebuilding.

### P07-I05 — Implement: Conversation dashboard and retention

Derive transcripts from checkpoints, implement pagination/read projections and retention/deletion jobs with tenant-scoped access.

### P07-T05 — Test: Conversation dashboard and retention

Test faithful reconstruction, projection rebuild, 90-day default retention, privacy deletion and access policy.

## Phase 08 — Streaming website widget and domain security

**Focus:** Deliver the installable cross-origin iframe widget, browser lifecycle, SSE transport and support actions.

**Exit deliverable:** A real website can install and use a chatbot safely.

### P08-I01 — Implement: Public widget config and allowed origins

Expose public-only published config; validate exact/wildcard hosts, test-mode origins and signed/opaque tab session identifiers.

### P08-T01 — Test: Public widget config and allowed origins

Test host matching, spoofed IDs, forbidden domains, public-data minimization and tenant isolation.

### P08-I02 — Implement: Embeddable loader and isolated iframe

Create versioned JS snippet, floating/inline modes, cross-origin iframe and validated postMessage contract.

### P08-T02 — Test: Embeddable loader and isolated iframe

Test iframe isolation, message-origin checks, installation paths, responsive rendering and CSP cases.

### P08-I03 — Implement: SSE generation and reconnect recovery

Stream partial/completed/error events while server work survives disconnect; reconnect reads completed authoritative checkpoint response.

### P08-T03 — Test: SSE generation and reconnect recovery

Test event ordering, disconnect/reconnect, exactly-once persistence, duplicate submits and credit settlement.

### P08-I04 — Implement: Branding, availability and support actions

Apply published widget styles, automatic/forced availability, business hours, offline links and optional contact form.

### P08-T04 — Test: Branding, availability and support actions

Test schedule overrides, timezone boundaries, offline enforcement, styling and spam controls.

### P08-I05 — Implement: Layered abuse protection and browser E2E

Implement IP/session/chatbot/org rate limits and optional challenges; run browser journeys in Playwright.

### P08-T05 — Test: Layered abuse protection and browser E2E

Test distributed limits, rate-limit errors, mobile/keyboard accessibility, refresh and tab isolation.

## Phase 09 — Answer inspection, operations and privacy

**Focus:** Make retrieval evidence, model behavior and tenant activity observable without exposing secrets.

**Exit deliverable:** An auditable dashboard and operational telemetry.

### P09-I01 — Implement: Durable answer evidence and trace schema

Record query rewrites, candidate/selected chunks, source snapshots, model versions, costs and execution identifiers.

### P09-T01 — Test: Durable answer evidence and trace schema

Test trace completeness, source deletion snapshots, idempotent trace linkage and sensitive-field redaction.

### P09-I02 — Implement: Inspection dashboard and authorization

Build transcript/trace views, effective context inspection and chatbot-management permission enforcement.

### P09-T02 — Test: Inspection dashboard and authorization

Test RBAC, cross-tenant trace access, safe rendering and historical configuration resolution.

### P09-I03 — Implement: Observability and data lifecycle jobs

Add structured logs, correlation IDs, Celery monitoring, retention cleanup and recovery metrics.

### P09-T03 — Test: Observability and data lifecycle jobs

Test correlation propagation, retention cleanup, failure alerts and privacy deletion across projections.

## Phase 10 — Internationalization and customer-ready dashboard

**Focus:** Complete localized management journeys and the full chatbot customization experience.

**Exit deliverable:** A coherent multilingual product interface.

### P10-I01 — Implement: Localization infrastructure and RTL

Introduce translation catalogs, locale negotiation, localized validation, timezone presentation and RTL templates.

### P10-T01 — Test: Localization infrastructure and RTL

Test locale fallback, translation coverage, RTL markup and missing translations.

### P10-I02 — Implement: End-to-end management workflows

Complete dashboard overview, chatbot, knowledge, conversation, usage, organization and support workflows.

### P10-T02 — Test: End-to-end management workflows

Test cross-page user journeys, empty states, permissions, HTMX behavior and accessibility.

### P10-I03 — Implement: Usage and credit reporting

Expose credit grants, reservations, consumption, model cost and limits by organization/chatbot.

### P10-T03 — Test: Usage and credit reporting

Test reconciliation against ledger, concurrent activity and authorization.

## Phase 11 — Payments and subscription lifecycle

**Focus:** Integrate a verified international payment provider only after onboarding/legal feasibility is resolved.

**Exit deliverable:** Paid subscriptions with reliable entitlements and webhooks.

### P11-I01 — Implement: Payment-provider selection and adapter

Validate merchant eligibility, payouts, tax responsibilities and provider contracts; implement provider adapter and checkout.

### P11-T01 — Test: Payment-provider selection and adapter

Test adapter contracts, checkout authorization, currency validation and provider failures.

### P11-I02 — Implement: Webhook-driven subscription transitions

Verify webhook signatures, deduplicate events, reconcile out-of-order updates and update entitlement effective dates.

### P11-T02 — Test: Webhook-driven subscription transitions

Test replay, duplicates, out-of-order delivery, grace/cancellation and failed renewals.

### P11-I03 — Implement: Billing portal and paid-launch gates

Build invoices/subscription UI, downgrade checks, support/refund flows and operational reconciliation.

### P11-T03 — Test: Billing portal and paid-launch gates

Test checkout-to-entitlement E2E, payment failure recovery, downgrade rejection and accounting consistency.

## Phase 12 — Production Compose, operations and release

**Focus:** Promote the same container architecture to a secure, observable, recoverable production deployment. Docker Compose remains the deployment mechanism; Nginx is the mandatory public ingress.

**Exit deliverable:** A repeatably deployed production candidate with HTTPS, isolated internal services, tested rollback and backups, and measurable security/performance gates.

### P12-I01 — Implement: Production Compose topology and immutable images

Create `compose.prod.yaml` extending the shared `compose.yaml`. Build/pin production-ready images, disable reload/bind mounts, configure Nginx as sole public service, internal Docker networks, PostgreSQL persistent storage, Redis, Celery worker/Beat as required, resource limits, health checks and restart policies. Define explicit Alembic migration execution and deploy/rollback procedure; avoid treating `depends_on` as application readiness or Compose as automatic multi-host HA.

### P12-T01 — Test: Production Compose contracts and deploy lifecycle

Use pytest to validate rendered production Compose configuration, published ports, environment requirements, health endpoints through Nginx, startup sequencing, migration idempotency, deploy/rollback smoke paths and data persistence across ordinary container recreation. Run on isolated disposable infrastructure.

### P12-I02 — Implement: Nginx HTTPS, SSE and proxy hardening

Configure valid TLS certificates, HTTPS redirect, security headers, trusted forwarded IP/protocol, host restrictions, upload body limits, static assets and SSE routes with buffering disabled and appropriate read/send timeouts. Explain proxy header spoofing, real client IP, cookie security and origin checks; Nginx rate limiting complements, but does not replace, application-layer per-tenant/session limits.

### P12-T02 — Test: TLS, routing and streaming under the production proxy

Run pytest HTTP/TLS checks through Nginx for redirect, headers, allowed hosts, client-IP trust, oversized upload rejection, static assets and incremental SSE delivery including disconnect/reconnect. Verify internal ports are not externally reachable in the test deployment.

### P12-I03 — Implement: Backups, recovery, secrets and observability

Configure secret injection, log retention, structured service logs, database/object-storage backups, restore runbooks, container/image update strategy, monitoring and alerting. Define RPO/RTO and explicitly test that backup/restore includes checkpoint-authoritative conversations, credit ledger, embeddings and uploaded files. Keep backup credentials separate from application credentials.

### P12-T03 — Test: Disaster recovery and operations

Use pytest integration checks and documented restore drills to verify backup integrity, restored conversation history, credits, document references, retention cleanup and service readiness. Simulate worker/process interruption and confirm idempotent recovery; check no secrets leak into logs or artifacts.

### P12-I04 — Implement: Load, resilience, security and cost budgets

Benchmark concurrent widget sessions, Nginx streaming connections, PostgreSQL/pgvector filtering, checkpoint growth, Celery worker throughput, and credit-reservation contention. Review CSRF/CSP, cross-tenant access, prompt injection, upload safety and data deletion. Establish measurable performance and budget thresholds before public launch.

### P12-T04 — Test: Performance and adversarial boundaries

Run pytest security/integration suites plus dedicated load tooling for realistic concurrency. Verify tenant isolation, rate limits, credit accounting, graceful failure, bounded resource use and no streaming proxy buffering. Record latency/cost and recovery evidence.

### P12-I05 — Implement: Release readiness and operational handoff

Complete production runbooks, health/alert dashboard, environment checklist, migration and rollback playbook, incident response, privacy review, paid-launch payment gate and acceptance checklist. Validate all core journeys through Nginx and document known operational limitations of single-host Compose.

### P12-T05 — Test: Full release regression and recovery rehearsal

Run all pytest suites, Playwright browser tests, retrieval-quality evaluations, staging deployment smoke tests, TLS/SSE verification and full backup/restore rehearsal. Confirm no paid customer onboarding until live payment integration and webhook verification are complete.

## Required testing architecture

- **Test ownership and discovery:** Place each feature's tests and fixtures in `src/chathat/<feature>/tests/`. Running pytest from the repository root must discover the feature suites locally and in the application test container.
- **Fast unit tests:** Pure rules, state machines, RBAC policy, RRF, chunking, summary window and credit arithmetic; use pytest parametrization and simple fakes.
- **API tests:** `httpx.AsyncClient` + `ASGITransport`, application dependency overrides and authenticated/unauthenticated sessions; validate HTTP contracts, authorization and response shapes.
- **Database integration:** Isolated disposable PostgreSQL with pgvector and actual Alembic migrations. Verify constraints, transaction rollback, concurrency and tenant filters. Avoid SQLite as a substitute for PostgreSQL behavior.
- **Worker integration:** Add Redis and Celery services to Compose in Phase 05 (and Celery Beat when scheduled jobs are implemented); use a real test worker against isolated DB and object storage adapter; test retries, duplicate delivery and eventual cleanup. Eager-mode tests alone do not validate queue semantics.
- **Graph/model tests:** Deterministic fake model/embedding adapters for branch contracts; actual LangGraph PostgreSQL checkpoint integration tests for restoration, retention, and concurrency.
- **Browser end-to-end:** Playwright plus pytest integration for loader, iframe, HTMX, SSE, tab lifecycle, RTL and mobile behavior.
- **Performance/security:** Explicit pytest markers (`unit`, `integration`, `e2e`, `slow`, `security`) and separate CI jobs; performance baselines and dedicated load tooling for realistic concurrency.

## Docker Compose execution contract

- **Standard development:** `docker compose -f compose.yaml -f compose.dev.yaml up --build -d`; access the application through Nginx.
- **Tests:** Run `pytest` inside a disposable application/test service with isolated test DB/Redis. Example command (final service names determined in Phase 01): `docker compose -f compose.yaml -f compose.dev.yaml -f compose.test.yaml run --rm api pytest`. Never point the test database at the development or production database.
- **Migrations:** Run Alembic in the application container using a one-off command and explicit environment; production migrations are a controlled deployment step.
- **Production:** `docker compose -f compose.yaml -f compose.prod.yaml ...` with Nginx as sole public HTTP ingress; no source bind mounts or development reload.
- **Network:** Database, Redis, Celery and FastAPI ports stay internal in production. Nginx handles HTTP routing, static assets, TLS and SSE proxy settings.
- **Progressive services:** Nginx/API/PostgreSQL start in Phase 01; Redis/Celery join when ingestion starts; Celery Beat joins when periodic scheduling is implemented.
- **Testing discipline:** Each implementation lesson is immediately followed by pytest verification of the implemented behavior, including container/network contracts where relevant. Supplementary `docker compose config`, `nginx -t`, and deployment shell checks do not replace pytest.

## Recommended lesson execution protocol

1. Inspect current repository files and relevant specification requirements; state what already exists.
2. Explain the feature contract and the smallest runnable vertical increment.
3. Type implementation in small logical sections; explain execution and why each choice was made.
4. Run the implementation demonstration and note failure/rollback behavior.
5. Immediately teach the paired pytest lesson; run its tests and fix defects before proceeding.
6. Record changed files, commands, acceptance criteria, and any open implementation decisions; avoid automatic repo writes unless authorized.
7. End each phase with a demonstration and update implementation status based on actual tests, not assumption.

## Critical dependencies and design checkpoints

- **Before Phase 01:** Ensure Docker Engine with Docker Compose plugin is available. Host Python, PostgreSQL, Redis and Nginx are not prerequisites.
- **Before Phase 03:** Choose a provisional internal credit conversion rule for development; keep it versioned/configurable, not hardcoded into business logic.
- **Before Phase 05:** Introduce Redis/Celery through Compose and select object storage and an embedding model, confirm dimensions/multilingual suitability and ingestion resource limits.
- **Before Phase 06:** Select managed primary/fallback LLM providers and validate compatible response/usage contracts.
- **Before Phase 07:** Run the LangGraph checkpoint contract spike first. Do not assume checkpoint replay, history storage, or transactions satisfy Q058/Q061 without verification; revise implementation design if tests reveal incompatibility.
- **Before Phase 08:** Define host origin validation, iframe messaging, CSP, tab session restoration and reconnect contracts in executable tests.
- **Before Phase 11:** Confirm merchant eligibility, tax/legal obligations and payment provider; keep manual provisioning available for test environments.
- **Before Phase 12:** Prepare production Compose overrides, Nginx TLS certificates, deployment secrets and backup storage; establish measurable latency, error, RAG-quality, cost, backup and recovery release gates.

## Deliberate sequencing choices

- **Containerized Nginx ingress is introduced before feature endpoints** so development exercises the real reverse-proxy boundary and SSE constraints from the beginning.
- **Tenant isolation precedes documents and conversations** because retrofitting tenant ownership creates expensive security and migration risk.
- **Entitlements and credits precede model calls** because AI operations have real costs and require concurrency-safe reservations from the first production-like flow.
- **Knowledge-base relationships precede ingestion** so canonical documents can be reused correctly from the outset.
- **A minimal stateless RAG graph precedes durable conversation memory** to make retrieval and generation independently testable.
- **Checkpoint contract verification precedes long-thread implementation** because Q058/Q061 demand complete original history in checkpoint authority.
- **Widget streaming follows conversation durability** so reconnect behavior is built on real persisted operation state, not temporary in-memory workarounds.
- **Payment provider integration is late, not billing logic** in accordance with Q060.

## Definition of done for every implementation/test pair

- The new behavior has a documented input/output/error contract and runs through the established Docker Compose environment.
- Tests demonstrate normal behavior, the main failure path, and tenant/security boundaries where applicable.
- All relevant existing tests remain green; no unrelated regression is accepted.
- Database changes have migrations; operations that can retry are idempotent.
- Secrets are never placed in client assets, test snapshots or logs.
- Code and tests are understandable enough for the learner to explain the execution flow without memorizing implementation details.

## Revision history

| Date | Revision | Change |
|---|---|---|
| 2026-11-08 | 1.1 | Regenerated from latest GitHub specification: Docker Compose for development and production, dedicated Nginx service, containerized pytest/Alembic, production TLS/SSE, backup and deployment tests. Expanded to 106 alternating lessons. |
| 2026-11-11 | 1.2 | Added P01-I07 and P01-T07 before Docker setup to adopt TECH-014. The curriculum now has 108 lessons. |
