# ChatHat — Implementation Curriculum and Phase Plan

> **Status:** Proposed implementation curriculum; implementation progress is tracked separately.  
> **Baseline:** `docs/chathat-spec.md` v0.3.0, decisions Q001–Q061.  
> **Repository:** https://github.com/EslamKamel89/ChatHat  
> **Created:** 2026-11-08  
> **Repository inspection:** At planning time, the repository contained `docs/chathat-spec.md` and `docs/questions_and_answers.md`, with no application code.

## Teaching contract

Each feature is delivered as a strict **implementation lesson immediately followed by a pytest lesson**. Do not start another implementation lesson until its paired tests pass. The instructor teaches by incrementally typing production-quality code and explaining *why* each significant construct exists, what executes at runtime, how data moves, failure behavior, and trade-offs. Avoid unexplained code dumps and elementary Python/FastAPI introductions.

Each **implementation lesson** must include: purpose and prerequisite contracts; precise files to create/edit; incremental code chunks; explanations of imports, annotations, dependencies, async boundaries, transactions and lifecycle where relevant; one runnable demonstration; design alternatives; and a short change summary. Show complete final code only when necessary to make the increment runnable. Never silently modify files or infer repository state: inspect GitHub before each lesson.

Each **testing lesson** must include: the contract from the previous lesson; pytest fixture design; unit vs integration test rationale; happy path, important negative paths, permissions and boundary cases; executable tests; exact commands and expected results; and an explanation of what each assertion proves. Use real PostgreSQL/pgvector, Redis and Celery for relevant integration tests rather than substituting mocks for critical boundaries. Use mocks/fakes only at genuine external ports (LLM, OAuth, payment providers, object storage where appropriate). Tests must be deterministic, independent and safe to rerun.

**Naming:** `Pxx-Iyy` = implementation; `Pxx-Tyy` = its immediately following test lesson. A phase is complete only after all paired tests pass, migrations work from a clean database, and the phase's end-to-end increment is demonstrable.

**Non-negotiable architecture:** Shared PostgreSQL tables with strict tenant isolation (Q056); canonical document embeddings across KBs (Q057); complete original messages in authoritative LangGraph checkpoint state with derived context and transcripts (Q058/Q061); monthly AI credits with atomic reservations and measured settlement (Q059); manual plan provisioning before paid launch, payment integration before charging customers (Q060). Keep separate trace/evidence snapshots as required by the spec, without creating a second authoritative conversation transcript.

**Scope gates, not extra questionnaires:** Before implementing provider-specific integrations, select a compatible provider and validate contracts. Before production release, resolve payment eligibility, data protection, retention, operational budgets and measurable release thresholds. These do not block planning or the early phases.

## Curriculum map

| Phase | Focus | Implementation lessons | Pytest lessons | Total |
|---|---|---:|---:|---:|
| 01 — Application foundation and engineering workflow | Create a reproducible FastAPI project, development infrastructure, configuration and migration lifecycle. | 4 | 4 | 8 |
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
| 12 — Production deployment, performance and release | Harden the complete system and release against measurable security, reliability and cost gates. | 4 | 4 | 8 |
| **Total** | | **50** | **50** | **100** |

## Phase 01 — Application foundation and engineering workflow

**Focus:** Create a reproducible FastAPI project, development infrastructure, configuration and migration lifecycle.

**Exit deliverable:** A bootable service with automated smoke tests.

### P01-I01 — Implement: Project skeleton and application factory

Create pyproject.toml, src/chathat package, FastAPI app factory, routers, lifespan, health endpoints and dependency boundaries.

### P01-T01 — Test: Project skeleton and application factory

Test app startup/shutdown, health response, routing and lifespan failure with TestClient/ASGITransport.

### P01-I02 — Implement: Typed settings and environment boundaries

Use pydantic-settings, environment-specific configuration, secret handling and dependency overrides; avoid global mutable state.

### P01-T02 — Test: Typed settings and environment boundaries

Test configuration precedence, invalid settings, secret redaction and override isolation.

### P01-I03 — Implement: PostgreSQL, SQLModel and Alembic baseline

Wire async database engine/session ownership, SQLModel metadata, Alembic migrations and pgvector extension prerequisites.

### P01-T03 — Test: PostgreSQL, SQLModel and Alembic baseline

Run migrations against disposable PostgreSQL; verify upgrade, constraints, session rollback and schema consistency.

### P01-I04 — Implement: Development tooling and CI

Add Docker Compose for PostgreSQL/Redis, lint/type checks, pytest configuration, coverage reporting and GitHub Actions.

### P01-T04 — Test: Development tooling and CI

Test CI smoke path, fixture isolation and reproducible database setup; enforce green checks.

## Phase 02 — Organizations, identity and authorization

**Focus:** Establish shared-table multi-tenancy and secure organization-level access before introducing tenant-owned features.

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

## Phase 12 — Production deployment, performance and release

**Focus:** Harden the complete system and release against measurable security, reliability and cost gates.

**Exit deliverable:** A deployed, monitored, recoverable production candidate.

### P12-I01 — Implement: Production infrastructure and deployment

Provision API/worker/database/Redis/object storage, TLS, secrets, migrations, asset CDN and rollback pipeline.

### P12-T01 — Test: Production infrastructure and deployment

Test deploy/rollback, migration safety, environment isolation, secrets and startup readiness.

### P12-I02 — Implement: Load, resilience and cost budgets

Benchmark concurrent widget chats, checkpoint growth, vector retrieval, Celery load and credit ceilings.

### P12-T02 — Test: Load, resilience and cost budgets

Run pytest-based performance/integration suites plus dedicated load tools; validate limits and failure recovery.

### P12-I03 — Implement: Security and privacy review

Audit tenant boundaries, uploads, injection resistance, CSRF/CSP, data retention, backups and incident response.

### P12-T03 — Test: Security and privacy review

Run adversarial pytest scenarios, dependency scans and deletion/restore drills.

### P12-I04 — Implement: Release acceptance and operational handoff

Complete core user journey, RAG evaluation fixtures, runbooks, alerts, monitoring and launch checklist.

### P12-T04 — Test: Release acceptance and operational handoff

Execute full regression, retrieval-quality evaluation, smoke tests and disaster-recovery rehearsal.

## Required testing architecture

- **Fast unit tests:** Pure rules, state machines, RBAC policy, RRF, chunking, summary window and credit arithmetic; use pytest parametrization and simple fakes.
- **API tests:** `httpx.AsyncClient` + `ASGITransport`, application dependency overrides and authenticated/unauthenticated sessions; validate HTTP contracts, authorization and response shapes.
- **Database integration:** Isolated disposable PostgreSQL with pgvector and actual Alembic migrations. Verify constraints, transaction rollback, concurrency and tenant filters. Avoid SQLite as a substitute for PostgreSQL behavior.
- **Worker integration:** Redis/Celery test worker against isolated DB and object storage adapter; test retries, duplicate delivery and eventual cleanup. Eager-mode tests alone do not validate queue semantics.
- **Graph/model tests:** Deterministic fake model/embedding adapters for branch contracts; actual LangGraph PostgreSQL checkpoint integration tests for restoration, retention, and concurrency.
- **Browser end-to-end:** Playwright plus pytest integration for loader, iframe, HTMX, SSE, tab lifecycle, RTL and mobile behavior.
- **Performance/security:** Explicit pytest markers (`unit`, `integration`, `e2e`, `slow`, `security`) and separate CI jobs; performance baselines and dedicated load tooling for realistic concurrency.

## Recommended lesson execution protocol

1. Inspect current repository files and relevant specification requirements; state what already exists.
2. Explain the feature contract and the smallest runnable vertical increment.
3. Type implementation in small logical sections; explain execution and why each choice was made.
4. Run the implementation demonstration and note failure/rollback behavior.
5. Immediately teach the paired pytest lesson; run its tests and fix defects before proceeding.
6. Record changed files, commands, acceptance criteria, and any open implementation decisions; avoid automatic repo writes unless authorized.
7. End each phase with a demonstration and update implementation status based on actual tests, not assumption.

## Critical dependencies and design checkpoints

- **Before Phase 03:** Choose a provisional internal credit conversion rule for development; keep it versioned/configurable, not hardcoded into business logic.
- **Before Phase 05:** Select object storage and an embedding model, confirm dimensions/multilingual suitability and ingestion resource limits.
- **Before Phase 06:** Select managed primary/fallback LLM providers and validate compatible response/usage contracts.
- **Before Phase 07:** Run the LangGraph checkpoint contract spike first. Do not assume checkpoint replay, history storage, or transactions satisfy Q058/Q061 without verification; revise implementation design if tests reveal incompatibility.
- **Before Phase 08:** Define host origin validation, iframe messaging, CSP, tab session restoration and reconnect contracts in executable tests.
- **Before Phase 11:** Confirm merchant eligibility, tax/legal obligations and payment provider; keep manual provisioning available for test environments.
- **Before Phase 12:** Establish measurable latency, error, RAG-quality, cost, backup and recovery release gates.

## Deliberate sequencing choices

- **Tenant isolation precedes documents and conversations** because retrofitting tenant ownership creates expensive security and migration risk.
- **Entitlements and credits precede model calls** because AI operations have real costs and require concurrency-safe reservations from the first production-like flow.
- **Knowledge-base relationships precede ingestion** so canonical documents can be reused correctly from the outset.
- **A minimal stateless RAG graph precedes durable conversation memory** to make retrieval and generation independently testable.
- **Checkpoint contract verification precedes long-thread implementation** because Q058/Q061 demand complete original history in checkpoint authority.
- **Widget streaming follows conversation durability** so reconnect behavior is built on real persisted operation state, not temporary in-memory workarounds.
- **Payment provider integration is late, not billing logic** in accordance with Q060.

## Definition of done for every implementation/test pair

- The new behavior has a documented input/output/error contract.
- Tests demonstrate normal behavior, the main failure path, and tenant/security boundaries where applicable.
- All relevant existing tests remain green; no unrelated regression is accepted.
- Database changes have migrations; operations that can retry are idempotent.
- Secrets are never placed in client assets, test snapshots or logs.
- Code and tests are understandable enough for the learner to explain the execution flow without memorizing implementation details.
