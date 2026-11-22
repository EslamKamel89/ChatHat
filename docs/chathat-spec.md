# ChatHat — Product Requirements Specification

> **Document version** 0.4.3\
> **Status** Draft with decisions Q001–Q061 and feature-based source organization incorporated\
> **Last updated** 2026-11-22\
> **Repository (code SSOT):** https://github.com/EslamKamel89/ChatHat  
> **Document role:** Product and behavioral requirements; not evidence that features are implemented.

## 0. Specification governance

### 0.1 Purpose

ChatHat is a multi-tenant, globally marketed SaaS that allows businesses to deploy an AI chatbot on an existing website by inserting a small script tag. Businesses upload knowledge files, configure chatbot behavior and rules, inspect conversations and retrieved evidence, and manage subscriptions. The system uses a retrieval-augmented generation (RAG) architecture and LangGraph for stateful AI orchestration.

ChatHat is also an intentionally educational production-grade project for practicing FastAPI and related technologies. Technical depth should not create unnecessary product complexity.

### 0.2 Requirement statuses

- **CONFIRMED:** Explicitly requested by the product owner.
- **PROPOSED:** Recommended working assumption; requires approval.
- **OPEN:** Unresolved decision; do not treat any option as final.
- **DEFERRED:** Considered but not included in the initial scope unless subsequently approved.

A requirement's status describes **decision certainty**, not implementation progress. Track implementation independently as `not started`, `in progress`, `implemented`, `verified`, or `blocked` when work begins.

### 0.3 Change procedure

1. Every interactive Q&A batch records question IDs, options, selected answers, rationale, and consequences.
2. Update only affected requirements, acceptance criteria, data contracts, and dependencies.
3. Keep stable requirement IDs; mark superseded requirements rather than silently deleting their history.
4. Record changes in the decision log and increment the document version.
5. When a decision conflicts with another requirement, flag the conflict before implementation.
6. Never infer code implementation from this specification. Inspect the latest GitHub repository state before code-level recommendations.

### 0.4 Priority definitions

- **P0:** Required for a secure, sellable core product.
- **P1:** Important enhancement; can follow the initial release.
- **P2:** Optional or future capability.

### 0.5 Sources of truth

- **GitHub repository:** Current source code, migrations, configuration, tests, and implementation reality.
- **SPEC.md:** Agreed product behavior, constraints, and acceptance criteria.
- **Future architecture decision records (ADRs):** Decisions and trade-offs that cannot be expressed as requirements alone.
- **External provider documentation:** Actual supported capabilities and integration contracts; verify versions before implementation.

If specification and code disagree, report the discrepancy rather than silently changing either.

---

## 1. Product vision and boundaries

**PRD-001 [CONFIRMED, P0]** ChatHat shall allow a business to add an AI chatbot to an already running website using a script tag, without requiring changes to the business's backend.

**PRD-002 [CONFIRMED, P0]** Businesses shall upload files that supply the chatbot's knowledge.

**PRD-003 [CONFIRMED, P0]** Businesses shall configure rules governing chatbot behavior.

**PRD-004 [CONFIRMED, P0]** The chatbot shall answer using RAG, with tenant-specific knowledge retrieval.

**PRD-005 [CONFIRMED, P0]** Businesses shall inspect individual answers and the context retrieved by similarity search for debugging.

**PRD-006 [CONFIRMED, P0]** ChatHat shall be designed as a SaaS for customers in multiple countries, with international payment handling as a first-class concern.

**PRD-007 [CONFIRMED, P0]** General-purpose AI website chatbot SaaS with selectable industry templates.

**PRD-008 [PROPOSED, P0]** The MVP shall emphasize accurate, grounded responses, ease of installation, predictable costs, and traceability rather than autonomous task execution.

**PRD-009 [CONFIRMED, P0]** The initial product is general-purpose, with optional industry-specific templates and platform-managed retrieval pipelines.

**PRD-010 [CONFIRMED, P0]** Dashboard and chatbot support full localization in customer-selected supported languages, including RTL; initial language list remains OPEN.

### 1.1 Users and roles

- **Platform operator:** Operates ChatHat, reviews aggregate service health, handles billing incidents and abuse, and administers platform settings.
- **Organization owner:** Manages subscription, organization membership, and chatbot ownership.
- **Organization member:** Manages permitted chatbot configuration, knowledge, and conversations.
- **Website visitor:** Interacts with a public chatbot without necessarily creating a ChatHat account.

**USR-001 [CONFIRMED, P0]** Organization is the tenant; its creator becomes an owner with full permissions and can invite additional owners or restricted members.

**USR-002 [CONFIRMED, P0]** Organization owners create custom organization-scoped roles and assign permissions.

**USR-003 [CONFIRMED, P0]** Website visitors chat anonymously in tab-scoped sessions; normal same-tab refresh restores the conversation, but tab closure ends intentional resumability.

**USR-004 [CONFIRMED, P1]** Each registered dashboard user belongs to exactly one organization.

### 1.2 Core user journeys

1. Owner registers, creates an organization, and chooses a plan or trial.
2. Owner creates a chatbot, sets its identity, rules, and permitted website domains.
3. Owner uploads knowledge documents and observes ingestion progress.
4. Owner tests the chatbot in a dashboard preview.
5. Owner copies a script snippet into the website.
6. Visitor opens the widget and sends messages; the chatbot answers using tenant-scoped knowledge and conversation memory.
7. Owner reviews conversations, evidence, errors, and usage.
8. Owner updates documents and configuration; subsequent answers use the applicable published version.
9. Owner manages subscription, billing, and quotas.

---

## 2. Confirmed technology stack and engineering constraints

**TECH-001 [CONFIRMED, P0]** HTTP backend: FastAPI.

**TECH-002 [CONFIRMED, P0]** ORM and relational modeling: SQLModel; migrations: Alembic.

**TECH-003 [CONFIRMED, P0]** Primary relational database: PostgreSQL; vector similarity: pgvector.

**TECH-004 [CONFIRMED, P0]** Dashboard: Jinja2, HTMX, Alpine.js, Tailwind CSS, and daisyUI.

**TECH-005 [CONFIRMED, P0]** AI orchestration: LangGraph, using its supported built-in primitives rather than reimplementing equivalent framework features.

**TECH-006 [CONFIRMED, P0]** Durable LangGraph checkpointing for conversation continuity.

**TECH-007 [CONFIRMED, P0]** Celery for background processing.

**TECH-008 [PROPOSED, P0]** Redis as Celery broker; confirm result backend and task-monitoring strategy separately.

**TECH-009 [PROPOSED, P0]** S3-compatible object storage for uploaded source files.

**TECH-010 [PROPOSED, P0]** Modular monolith with separately deployable FastAPI and Celery processes.

**TECH-011 [PROPOSED, P0]** PostgreSQL checkpoint persistence via the supported LangGraph PostgreSQL saver integration. The implementation shall use compatible library versions and their documented initialization/migration procedures.

**TECH-012 [CONFIRMED, P0]** ChatHat centrally manages generation models and primary/backup providers; customers cannot select models or bring keys. Specific providers and embedding models remain OPEN.

**TECH-013 [OPEN, P0]** Hosting provider, deployment topology, secrets management, and infrastructure budget.

**TECH-014 [CONFIRMED, P0]** Organize ChatHat's FastAPI source by feature. Each feature owns its code and pytest tests in a single package under `src/chathat/`.

### 2.1 Engineering principles

- Preserve explicit boundaries between HTTP/API, business services, persistence, AI orchestration, background tasks, and third-party providers.
- Prefer small, testable modules over premature microservices.
- Use LangGraph for checkpointing, graph execution, and applicable memory tools; custom code is justified for product-specific contracts, audit records, tenant isolation, and retrieval diagnostics.
- Separate product requirements from specific library APIs. Verify current LangGraph recommendations at implementation time; do not assume that a particular agent or middleware API remains unchanged.
- Treat browser-provided chatbot IDs, thread IDs, and metadata as untrusted input.

### 2.2 Feature packages

- Keep each feature's routing, request and response schemas, models, services, controllers, and other feature-specific code in its package. Add modules as the feature needs them. FastAPI route handlers can serve as controllers.
- **Directory-only feature roots:** `src/chathat/core/` and every feature root `src/chathat/<feature>/` shall contain only directories as direct children, with `__init__.py` as the sole permitted direct file. Place all other authored files inside responsibility-based subdirectories, including Python modules, tests, and documentation. Feature roots may retain `__init__.py` as regular Python package markers. Responsibility subdirectories may contain files, including `__init__.py`. This rule does not apply to the application root `src/chathat/`, where `main.py` and `__init__.py` may remain. Generated or ignored runtime artifacts are outside this source-layout rule.
- Use `src/chathat/core/` for application-wide code such as health checks, lifespan, settings, and database session setup. Use `src/chathat/auth/` for authentication code such as sign-in, sessions, and identity dependencies when that feature is introduced.
- Keep the application factory in `src/chathat/main.py`. It assembles the FastAPI app and registers feature routers. Feature packages own their route definitions.
- Place each feature's pytest suite and feature-specific fixtures in `src/chathat/<feature>/tests/`. Group test modules into responsibility subpackages matching that feature, such as `tests/routes/`, `tests/services/`, `tests/models/`, `tests/settings/`, and `tests/database/`; do not maintain a flat list of test modules at the `tests/` root. Create groups as needed and include `__init__.py` package markers. Helpers belong with their responsibility, while shared fixtures belong in the nearest applicable `conftest.py`, including `tests/conftest.py` for feature-wide fixtures. Keep autouse fixture scope narrow.
- Core uses `tests/application/` for application behavior, `tests/settings/` for configuration, `tests/database/` for database integration and helpers, and `tests/infrastructure/` for Docker/Nginx integration whose configuration lives outside Python feature code. Pytest must discover all nested feature suites through the established development command `docker compose -f compose.yaml -f compose.dev.yaml exec api python -m pytest -v`, without special setup or an alternate trigger.

Use plural responsibility-based subpackages within each feature. Create them as their responsibilities are implemented.

| Subpackage | Responsibility |
| --- | --- |
| `routes/` | HTTP handlers and feature routers |
| `schemas/` | Request and response contracts |
| `models/` | Database entities owned by the feature |
| `services/` | Business workflows |
| `dependencies/` | FastAPI dependency providers |
| `settings/` | Typed configuration and environment validation, such as `core/settings/config.py` |
| `application/` | Application-instance setup, including `core/application/lifespan.py` |
| `tests/` | Feature tests grouped by responsibility; scoped helpers and `conftest.py` fixtures |

The approved authentication layout is the following target structure for the authentication lessons.

```text
src/chathat/auth/
├── __init__.py
├── routes/
│   ├── __init__.py
│   ├── sessions.py
│   └── oauth.py
├── schemas/
│   ├── __init__.py
│   └── sessions.py
├── models/
│   ├── __init__.py
│   └── users.py
├── services/
│   ├── __init__.py
│   └── authentication.py
├── dependencies/
│   ├── __init__.py
│   └── identity.py
└── tests/
    ├── __init__.py
    ├── conftest.py
    └── routes/
        ├── __init__.py
        ├── test_sessions.py
        └── test_oauth.py
```

Apply the same convention to core by placing the health router in `core/routes/health.py` and `HealthResponse` in `core/schemas/health.py`. Keep application lifespan in `core/application/lifespan.py`, typed settings in `core/settings/config.py`, dependency providers in `core/dependencies/`, and tests in `core/tests/`. Do not introduce direct files such as `core/settings.py`; `core/__init__.py` is permitted as the sole file exception.


---

## 3. Organizations, authentication, and authorization

**AUTH-001 [PROPOSED, P0]** The dashboard shall require authenticated users.

**AUTH-002 [CONFIRMED, P0]** Every organization-owned resource is authorized server-side within the authenticated organization. Shared PostgreSQL tables use an enforceable organization relationship; untrusted client-supplied organization IDs do not establish access (Q056).

**AUTH-003 [PROPOSED, P0]** A chatbot shall belong to exactly one organization at a time.

**AUTH-004 [CONFIRMED, P0]** All organization, document, conversation, checkpoint, trace, credit, and billing endpoints enforce server-side tenant authorization; hiding UI controls is insufficient (Q056).

**AUTH-005 [CONFIRMED, P0]** Tenant isolation applies to relational queries and vector retrieval, including organization and chatbot/knowledge-base membership filters (Q056–Q057).

**AUTH-006 [CONFIRMED, P0]** Support email/password and Google OAuth; verification, recovery and account-linking policies remain OPEN.

**AUTH-007 [CONFIRMED, P0]** Organization owners invite users and assign custom roles; chatbot management permission grants access to conversation transcripts and traces. Scope across chatbots remains OPEN.

**AUTH-008 [PROPOSED, P1]** Consider PostgreSQL row-level security as defense in depth after application-level tenant scoping is established and tested.

**AUTH-009 [CONFIRMED, P0]** Administrative actions affecting access, billing, credit allocation, manual plan provisioning, and deletion produce audit events (Q060).

### Acceptance criteria

- A member of organization A cannot access organization B's chatbot, documents, vector chunks, conversations, or traces by modifying IDs or API requests.
- Unauthenticated dashboard requests cannot read protected data.
- A public widget token/identifier cannot be used to call privileged management endpoints.

---

## 4. Chatbot configuration and lifecycle

**BOT-001 [PROPOSED, P0]** An organization may create and manage one or more chatbots, subject to plan limits.

**BOT-002 [CONFIRMED, P0]** Chatbot configuration includes editable template-copied prompts, rules, branding and settings, domains, support actions and availability controls.

**BOT-003 [PROPOSED, P0]** Chatbot rules shall be server-controlled and never writable by website visitors.

**BOT-004 [PROPOSED, P0]** Owners shall preview and test a chatbot before installing it.

**BOT-005 [CONFIRMED, P0]** Availability supports automatic business-hours scheduling plus forced-online and forced-offline manual overrides, each persisting until removed.

**BOT-006 [CONFIRMED, P0]** Reusable organization knowledge bases attach to multiple chatbots; organization-library documents attach to multiple knowledge bases without duplicate embeddings.

**BOT-007 [CONFIRMED, P1]** Draft/Publish configuration versions affect new conversations and subsequent messages in existing conversations; historical traces record the effective version.

**BOT-008 [CONFIRMED, P1]** Customers configure name, logo, welcome message, colors, position, fonts, dimensions, launcher icon and message styles; custom CSS is not required.

**BOT-009 [PROPOSED, P0]** Rules shall distinguish mandatory safety/operational policies from editable business guidance; tenant instructions cannot override platform-enforced isolation and security controls.

### Acceptance criteria

- A newly created chatbot can be configured and tested without installation.
- Disabling a chatbot prevents new public conversations according to the agreed policy.
- A visitor cannot change the chatbot's rules through a crafted message or request.

---

## 5. Website embedding and public widget

**WID-001 [CONFIRMED, P0]** A customer shall install the chatbot by adding a script tag to an existing website.

**WID-002 [CONFIRMED, P0]** A public-ID JavaScript snippet supports floating widget installation and optional inline mounting in a custom HTML container.

**WID-003 [CONFIRMED, P0]** A lightweight JavaScript loader renders the widget inside a cross-origin iframe for both floating and inline modes.

**WID-004 [PROPOSED, P0]** The widget shall support responsive desktop and mobile layouts, keyboard interaction, accessible labels, and loading/error states.

**WID-005 [CONFIRMED, P0]** Enforce layered IP, visitor-session, chatbot and organization rate limits, plan quotas and optional abuse challenges.

**WID-006 [CONFIRMED, P0]** Production usage is restricted to registered exact hostnames and explicitly configured wildcard subdomains; localhost/staging have a separate testing mode. Origin checks alone are not authentication.

**WID-007 [CONFIRMED, P0]** Stream answers over SSE independently of server-side generation lifetime; browser disconnect does not cancel generation. Persist completion once to authoritative LangGraph checkpoint state and restore it on same-tab reconnect (Q050, Q054, Q061).

**WID-008 [CONFIRMED, P0]** Anonymous conversations survive same-tab refresh but are not intentionally resumed after tab closure; duplicate-tab and browser-restore details remain OPEN.

**WID-009 [OPEN, P1]** Whether chat can be opened programmatically, prefilled with context, or linked to the host website's logged-in user.

**WID-010 [PROPOSED, P0]** Widget deployment shall use versioned, cacheable assets and a backwards-compatible public integration contract.

**WID-011 [OPEN, P0]** Host-page CSP compatibility, cookie/storage policy, cross-origin messaging protocol, and installation verification.

### Acceptance criteria

- Adding the snippet to a basic third-party page displays the widget without changing the host page's styling.
- A visitor can open, close, and use the widget on desktop and mobile.
- Exposed public IDs do not grant dashboard privileges.
- Widget errors do not break the host page.

---

## 6. Document management and ingestion

**DOC-001 [CONFIRMED, P0]** Customers shall upload knowledge files from the dashboard.

**DOC-002 [CONFIRMED, P0]** MVP formats are PDF, DOCX, TXT, Markdown, CSV, XLSX and HTML; file size limits depend on plan.

**DOC-003 [PROPOSED, P0]** Source files shall be stored outside the primary database in object storage, with metadata and processing state in PostgreSQL.

**DOC-004 [PROPOSED, P0]** Upload processing shall be asynchronous through Celery.

**DOC-005 [PROPOSED, P0]** Ingestion stages shall include validation, extraction, normalization, chunking, embedding, vector persistence, and publication.

**DOC-006 [PROPOSED, P0]** Each document shall expose processing state (`pending`, `processing`, `ready`, `failed`, `deleting`) and useful error details without leaking sensitive internals.

**DOC-007 [CONFIRMED, P0]** An organization owns canonical source documents and canonical chunks/embeddings per document and embedding-model version. Knowledge bases reference shared documents/chunks; attaching to another knowledge base does not re-embed (Q012, Q057).

**DOC-008 [CONFIRMED, P0]** Ingestion atomically publishes a complete canonical document/chunk/embedding version to its attached knowledge bases; unreadable scanned-PDF pages may be skipped/reported when readable pages remain (Q011, Q018, Q021, Q057).

**DOC-009 [CONFIRMED, P0]** Retain failed source uploads and attempt reports; retry idempotently without re-upload. Block exact duplicate source files per organization and reuse existing canonical embeddings across additional knowledge bases (Q019, Q022, Q023, Q057).

**DOC-010 [CONFIRMED, P0]** Replacement creates a new document. Global deletion immediately excludes the old document from every knowledge base and retrieval, then asynchronously cleans up canonical chunks/embeddings; detaching one knowledge-base reference alone must not delete shared embeddings. Historical trace evidence follows retention rules (Q015, Q016, Q024, Q057).

**DOC-011 [CONFIRMED, P0]** Document counts, individual file size, storage and related limits depend on subscription plan; numerical values remain OPEN.

**DOC-012 [CONFIRMED, P1]** Skip and report unreadable scanned-PDF pages without OCR; PDFs with zero readable text cannot publish. Other ingestion sources remain OPEN or DEFERRED.

**DOC-013 [OPEN, P0]** Choose chunking method, sizes, embedding model/dimensionality, and multilingual handling before ingestion implementation. Canonical embeddings are shared per document and embedding-model version, with explicit re-embedding/version migration (Q057).

**DOC-014 [PROPOSED, P0]** Uploads shall be checked for permitted type, content/size limits, path safety, and malicious content risks; parsers shall run with constrained resources.

### Acceptance criteria

- A valid file progresses from uploaded to ready, and its chunks are retrievable only for authorized chatbots.
- An invalid or unsupported file fails clearly without leaving partially published knowledge.
- A failed Celery task can be retried without duplicate searchable chunks.
- A document replacement does not expose an incomplete mixture of old and new chunks.

---

## 7. RAG retrieval and grounded generation

**RAG-001 [CONFIRMED, P0]** Retrieval is centrally managed by industry template; general-purpose retrieval combines pgvector similarity and PostgreSQL full-text search using Reciprocal Rank Fusion (RRF).

**RAG-002 [CONFIRMED, P0]** Retrieval enforces organization and authorized chatbot/knowledge-base membership filters before evidence is used; a shared document may be retrieved only through a knowledge base attached to the chatbot (Q056–Q057).

**RAG-003 [CONFIRMED, P0]** Trace original query, ambiguity decision, optional rewrite, branch rankings, fused RRF ranks, filters, evidence snapshots, source versions and effective configuration.

**RAG-004 [PROPOSED, P0]** The chatbot shall receive retrieved knowledge alongside applicable business rules and conversation context.

**RAG-005 [CONFIRMED, P0]** Use retrieval signals plus LLM assessment for evidence sufficiency; when unsupported, state the limitation without fabricating facts and offer configurable support links or an optional built-in contact form.

**RAG-006 [CONFIRMED, P0]** General-purpose retrieval uses hybrid vector/full-text RRF. Start with the latest visitor message and rewrite only when contextual ambiguity is detected; detailed parameters remain OPEN.

**RAG-007 [CONFIRMED, P1]** No citations are shown to website visitors; owners and authorized chatbot managers inspect internal evidence in the dashboard.

**RAG-008 [PROPOSED, P0]** Prompt-injection content inside documents and visitor messages shall be treated as untrusted data; it shall not gain authority to change system policies or access other tenants.

**RAG-009 [CONFIRMED, P0]** Use bounded retries and an overall deadline followed by a compatible backup provider; trace every attempt and return a safe temporary error on exhaustion.

**RAG-010 [CONFIRMED, P0]** ChatHat centrally selects and manages generation models/providers; customers cannot select models or supply provider API keys.

### Acceptance criteria

- A chatbot cannot retrieve another organization's chunks even if a visitor requests them explicitly.
- An answer trace identifies exactly which retrieved chunks were supplied to generation.
- Empty retrieval has a defined and testable behavior.
- Source document changes can be distinguished by version in historical traces.

---

## 8. LangGraph orchestration and conversation memory

### 8.1 Architectural distinction

LangGraph checkpointing stores recoverable graph/thread state. It does **not**, by itself, guarantee that a bounded verbatim window and rolling summary are the exact messages sent to the LLM. ChatHat must explicitly construct and test the model-input context. Framework-supported summarization or trimming components should be preferred where compatible with the selected graph architecture.

**MEM-001 [CONFIRMED, P0]** LangGraph shall orchestrate the conversation lifecycle using current, supported architectural patterns.

**MEM-002 [CONFIRMED, P0]** Durable LangGraph checkpoint state is the sole authoritative store of conversation history and response state, including complete original messages; model-input summaries and dashboard transcripts are derived representations (Q058, Q061).

**MEM-003 [CONFIRMED, P0]** The LLM receives recent verbatim user/assistant messages plus a rolling summary of older messages. This bounded model-input context is separate from the complete original history retained in authoritative checkpoint state (Q036, Q061).

**MEM-004 [CONFIRMED, P0]** The configured verbatim model-input window counts individual user and assistant messages, excluding system/tool messages. Older messages are summarized and the summary compressed to its token budget, without removing originals from authoritative checkpoint state (Q037, Q041, Q042, Q061).

**MEM-005 [CONFIRMED, P0]** Every checkpointed conversation/thread is bound server-side to a chatbot and organization; browser-supplied identifiers never grant access to another tenant’s checkpoint state (Q056, Q058).

**MEM-006 [PROPOSED, P0]** Model context shall be assembled from trusted system rules, rolling summary, recent verbatim messages, retrieved evidence, and the current user request, without unintentionally duplicating the current message.

**MEM-007 [CONFIRMED, P0]** Complete original user and assistant messages remain durably recoverable from authoritative LangGraph checkpoint state for their retention period. Dashboard transcripts are derived from checkpoints; optional query-optimized read projections must be rebuildable and are not independent authorities (Q058, Q061).

**MEM-008 [CONFIRMED, P0]** Synchronous summary updates merge each newly displaced message exactly once using a persisted cursor consistent with checkpoint state; failures cannot advance the cursor. Summarization never overwrites or discards original history (Q037, Q043, Q061).

**MEM-009 [CONFIRMED, P0]** Only one response-generation operation per conversation may run at a time. Server-side serialization and idempotency prevent duplicate generation or checkpointed assistant messages, including on SSE reconnection (Q039, Q054, Q061).

**MEM-010 [CONFIRMED, P0]** Before each answer generation, synchronously update the rolling summary and its cursor within the authoritative conversation-state transition. Verify checkpoint persistence and crash-recovery semantics before implementation (Q043, Q061).

**MEM-011 [CONFIRMED, P0]** Complete checkpoint-authoritative conversation history and associated debugging traces default to 90-day retention, configurable by organization within platform limits. Derived projections, checkpoint history, backups, and evidence deletion must follow the applicable privacy/retention lifecycle; exact cleanup implementation remains OPEN (Q044, Q058, Q061).

**MEM-012 [PROPOSED, P0]** Graph execution shall be observable by step and correlated to the answer's trace record.

**MEM-013 [OPEN, P1]** Whether long-term cross-conversation memory is required. A LangGraph Store is not required solely for thread checkpointing.

**MEM-014 [PROPOSED, P0]** Prefer a minimal, deterministic graph for retrieval and response generation; autonomous tool use shall be introduced only for approved product needs.

### 8.2 Logical message lifecycle

1. Authenticate/validate public chatbot and resolve authorized visitor conversation.
2. Restore thread state through the checkpointer.
3. Select the recent user/assistant verbatim window and synchronously merge displaced messages into the rolling summary; persist its cursor consistently.
4. Retrieve tenant-scoped evidence for the current query.
5. Build the effective model request and capture trace metadata.
6. Generate and stream the response using SSE; browser disconnection does not cancel server-side generation.
7. Persist assistant message, usage data, trace, and checkpoint under the defined consistency policy.
8. Maintain the configured verbatim window and bounded summary without modifying the full transcript.

The order of checkpoint commits, synchronous summary updates, trace writes and streaming-response persistence requires an explicit failure/recovery design before implementation.

### Acceptance criteria

- A restarted API process can continue a persisted conversation.
- Model input contains the intended recent messages exactly, with no missing, reordered, or duplicated turns.
- Older history is represented through a rolling summary once the threshold is exceeded.
- A long conversation remains within a configured context/token budget.
- Two concurrent messages cannot silently corrupt thread ordering.
- The original transcript remains available for the configured retention period even if graph state is summarized.

---

## 9. Conversation history, answer inspection, and observability

**DBG-001 [CONFIRMED, P0]** The SaaS dashboard shall allow inspection of individual chatbot answers and the context returned by similarity retrieval.

**DBG-002 [CONFIRMED, P0]** Answer traces correlate organization, chatbot, checkpointed conversation, original visitor message, checkpointed assistant response, and execution identifier; traces cannot become an independent authority for conversation history (Q058, Q061).

**DBG-003 [CONFIRMED, P0]** Trace original/rewritten queries, retrieval branch and fused ranks, sufficiency, immutable source evidence snapshots, effective configuration, provider/model, retries/failover, latency, errors, and usage, correlated to checkpointed messages (Q024, Q032–Q034, Q061).

**DBG-004 [PROPOSED, P0]** A trace shall distinguish retrieved candidate chunks from chunks actually passed to the LLM after filtering or truncation.

**DBG-005 [PROPOSED, P0]** Authorized users shall inspect effective model context or a privacy-safe representation; secrets and internal credentials must never appear in traces.

**DBG-006 [PROPOSED, P0]** Logs and traces shall use correlation IDs across FastAPI, LangGraph, Celery, and database operations.

**DBG-007 [OPEN, P0]** Whether to retain full prompts/model outputs, redact sensitive data, or use configurable trace levels.

**DBG-008 [OPEN, P1]** Answer feedback, evaluation datasets, regression tests, analytics dashboards, and automatic quality scoring.

**DBG-009 [CONFIRMED, P0]** Traces default to 90-day retention with organization-configurable periods within platform limits. Historical evidence remains after source deletion until expiry or privacy deletion, coordinated with checkpoint-history retention (Q024, Q044, Q061).

### Acceptance criteria

- An owner can open an answer and see the exact retrieved evidence used to generate it.
- A trace makes it possible to distinguish retrieval failure, context assembly failure, and generation failure.
- Users cannot inspect another tenant's traces.
- Debugging does not expose API keys or provider credentials.

---

## 10. Background processing and reliability

**JOB-001 [CONFIRMED, P0]** Celery shall execute background workloads.

**JOB-002 [PROPOSED, P0]** Ingestion, embedding generation, reindexing, and cleanup shall use background jobs where appropriate.

**JOB-003 [PROPOSED, P0]** Job records shall expose progress, status, timestamps, attempt count, and a safe error summary.

**JOB-004 [PROPOSED, P0]** Tasks shall be designed for at-least-once delivery: idempotency, bounded retries, and duplicate-safe writes.

**JOB-005 [PROPOSED, P0]** Large workloads shall be bounded by resource limits, tenant quotas, and worker concurrency.

**JOB-006 [OPEN, P0]** Queue topology, priorities, timeouts, result backend, dead-letter/failure handling, and monitoring tools.

**JOB-007 [PROPOSED, P0]** Tasks shall not rely on request-scoped database sessions or in-memory API state.

### Acceptance criteria

- Restarting a worker does not corrupt already published document data.
- Duplicate delivery does not create duplicate chunks or charge usage twice.
- Job failures are visible and actionable in the dashboard.

---

## 11. International billing, plans, and usage metering

**BILL-001 [CONFIRMED, P0]** The product shall support subscriptions and payments for an international customer base.

**BILL-002 [OPEN, P0]** Merchant of Record/payment provider selection, subject to actual onboarding and payout eligibility for an Egypt-based business, supported currencies, restricted markets, fees, tax responsibilities, and payout methods.

**BILL-003 [CONFIRMED, P0]** Plan entitlements and credit accounting are provider-independent; a payment-provider adapter is introduced before accepting paying customers (Q059–Q060).

**BILL-004 [PROPOSED, P0]** Before paid launch, synchronize paid subscriptions from verified, idempotently processed payment-provider webhooks. Core development and manually provisioned test plans do not depend on live payment integration (Q060).

**BILL-005 [CONFIRMED, P0]** Plans govern chatbot/document/file/storage limits and monthly AI credits. Downgrades are blocked until usage fits the destination plan; no automatic deletion. Credit enforcement applies to manually provisioned plans as well (Q020, Q025, Q059–Q060).

**BILL-006 [CONFIRMED, P0]** Subscription plans include a monthly AI-credit allowance. Exact prices, included credit amounts, overage/prepaid-credit policies, currencies, and tax presentation remain OPEN (Q059).

**BILL-007 [CONFIRMED, P0]** AI operations consume credits based on measured model/token usage. Reserve an estimated credit amount before execution and reconcile actual consumption after execution; failed operations, retries, and unused reservations require explicit settlement rules (Q059).

**BILL-008 [CONFIRMED, P0]** Check entitlements and atomically reserve available credits before chargeable AI work; finalize or release reservations with idempotent, concurrency-safe ledger operations. SSE disconnect does not by itself cancel server-side generation (Q054, Q059).

**BILL-009 [OPEN, P0]** Free trial, free tier, cancellation timing, proration, refunds, grace periods, and delinquency behavior.

**BILL-010 [PROPOSED, P0]** Billing records shall include provider event IDs, transaction references, entitlement effective dates, and reconciliation status.

**BILL-011 [PROPOSED, P0]** Provider webhooks shall verify signatures and handle duplicates, out-of-order delivery, and replay attempts.

**BILL-012 [OPEN, P0]** Regional restrictions, legal business entity, customer invoicing requirements, and customer support obligations.

### Acceptance criteria

- A successful payment activates the appropriate plan only after trusted payment confirmation.
- Replaying a webhook cannot create duplicate subscriptions or double-apply credits.
- A customer cannot exceed an enforced quota through simultaneous requests.
- Failed payment, cancellation, and plan changes produce predictable access behavior.

---

## 12. Data model — conceptual, not finalized SQL schema

| Entity                      | Key responsibilities                        | Decision status                          |
| --------------------------- | ------------------------------------------- | ---------------------------------------- |
| `organizations`             | Tenant identity, settings, lifecycle        | PROPOSED                                 |
| `users`                     | Dashboard identities                        | PROPOSED                                 |
| `memberships`               | User-to-organization roles                  | PROPOSED                                 |
| `chatbots`                  | Public chatbot identity and configuration   | PROPOSED                                 |
| `chatbot_domains`           | Allowed host origins/domains                | PROPOSED                                 |
| `documents`                 | Source file metadata and ownership          | PROPOSED                                 |
| `document_versions`         | Revisions and publication status            | PROPOSED                                 |
| `document_chunks`           | Chunk text, metadata, vectors               | PROPOSED                                 |
| `ingestion_jobs`            | Background progress and errors              | PROPOSED                                 |
| `visitor_sessions`          | Anonymous/session identity                  | OPEN                                     |
| `conversations`             | Tenant/chatbot/thread binding               | PROPOSED                                 |
| `conversation_messages`     | Verbatim transcript archive                 | PROPOSED                                 |
| `answer_traces`             | Execution and model metadata                | PROPOSED                                 |
| `retrieval_trace_chunks`    | Ranked retrieved evidence snapshots         | PROPOSED                                 |
| `plans`                     | Plan definitions and limits                 | PROPOSED                                 |
| `subscriptions`             | Provider-linked subscription state          | PROPOSED                                 |
| `usage_events`              | Idempotent metering ledger                  | PROPOSED                                 |
| `billing_webhook_events`    | Deduplicated provider event processing      | PROPOSED                                 |
| `audit_events`              | Sensitive configuration/access changes      | PROPOSED                                 |
| LangGraph checkpoint tables | Durable thread/graph state, framework-owned | CONFIRMED need; schema framework-managed |

**DATA-001 [CONFIRMED, P0]** Use shared PostgreSQL tables for tenants. Every tenant-owned row has an enforceable organization_id or a securely validated organization-owned parent; queries and constraints must prevent cross-tenant access (Q056).

**DATA-002 [PROPOSED, P0]** Database migrations for ChatHat-owned tables shall be managed through Alembic.

**DATA-003 [CONFIRMED, P0]** Use supported LangGraph checkpoint persistence as the sole authoritative conversation-history/response-state store. Verify full-state restoration, original-message retention, checkpoint write semantics, replay, and cleanup; do not recreate framework tables as SQLModel entities (Q058, Q061).

**DATA-004 [CONFIRMED, P0]** Represent canonical document chunks/embeddings per embedding-model version and many-to-many knowledge-base references; publication, detachment, global deletion, and cleanup must be safe for shared embeddings (Q057).

**DATA-005 [CONFIRMED, P0]** Maintain an idempotent, reconcilable AI-credit ledger for monthly allocation, reservation, measured consumption, release, and adjustment. Billing/credit ledger is not conversation transcript authority (Q059).

**DATA-006 [CONFIRMED, P0]** Initial multi-tenancy uses one shared PostgreSQL database and shared tables, with mandatory organization-scoped application authorization; separate per-tenant schemas/databases are not required (Q056).

**DATA-007 [OPEN, P0]** Vector indexing strategy and filtering/index performance as tenant and document counts grow.

---

## 13. API and interface contracts

These are conceptual endpoint groups, **not finalized routes**.

| Interface          | Responsibilities                                    |
| ------------------ | --------------------------------------------------- |
| Auth/session       | Sign in, sign out, verification, account recovery   |
| Organization       | Organization profile, members, permissions          |
| Chatbot management | CRUD, configuration, preview, publish/disable       |
| Knowledge          | Upload, list, replace, delete, ingestion status     |
| Public widget      | Bootstrap/config, visitor session, chat streaming   |
| Conversations      | List, view messages, search/filter                  |
| Answer inspection  | Trace metadata, retrieved evidence, model context   |
| Billing            | Checkout/session, plan changes, subscription status |
| Provider webhooks  | Verified, idempotent payment event intake           |
| Operations         | Health, readiness, monitoring, administrative tools |

**API-001 [PROPOSED, P0]** Dashboard endpoints shall enforce authenticated tenant authorization.

**API-002 [PROPOSED, P0]** Public widget endpoints shall expose only public configuration and permitted chat operations.

**API-003 [CONFIRMED, P0]** SSE exposes partial/completed/error states. On disconnect generation continues server-side; a completed assistant response is committed once to authoritative checkpoint state and recoverable within the same tab without regeneration (Q050, Q054, Q058, Q061).

**API-004 [PROPOSED, P0]** APIs shall return consistent error codes and validation details without leaking internal stack traces.

**API-005 [OPEN, P0]** REST route naming, API versioning, HTMX partial conventions, and public widget transport.

---

## 14. Dashboard experience

**UI-001 [CONFIRMED, P0]** The management dashboard shall use Jinja2, HTMX, Alpine.js, Tailwind CSS, and daisyUI.

**UI-002 [PROPOSED, P0]** Core sections: overview, chatbots, knowledge, conversations, answer inspection, usage, billing, and organization settings.

**UI-003 [PROPOSED, P0]** HTMX shall handle server-rendered partial updates where appropriate; Alpine.js shall handle localized client state without duplicating server authority.

**UI-004 [PROPOSED, P0]** Long-running ingestion and model operations shall expose progress and failure states.

**UI-005 [CONFIRMED, P0]** Fully localize dashboard and widget in customer-selected supported languages including RTL; exact initial language catalog remains OPEN.

**UI-006 [OPEN, P1]** Conversation export, bulk operations, advanced search, and analytics charts.

---

## 15. Security, privacy, and compliance

**SEC-001 [CONFIRMED, P0]** Enforce organization-scoped authorization in shared relational tables, canonical vector retrieval, LangGraph checkpoints, and traces; cross-tenant IDs must never bypass checks (Q056).

**SEC-002 [PROPOSED, P0]** Store provider API keys and other credentials server-side using appropriate secret management; never expose them to widget visitors.

**SEC-003 [PROPOSED, P0]** Enforce TLS, secure session cookies, CSRF protections for cookie-authenticated state changes, and relevant browser security headers.

**SEC-004 [PROPOSED, P0]** Validate uploads, constrain document parsing, and prevent file-path traversal and unauthorized file access.

**SEC-005 [CONFIRMED, P0]** Apply layered IP/session/chatbot/organization rate limits, optional challenges, domain restrictions and cost ceilings.

**SEC-006 [PROPOSED, P0]** Treat retrieved content, document text, and visitor prompts as untrusted with respect to platform instructions and tool permissions.

**SEC-007 [CONFIRMED, P0]** Checkpoint-authoritative transcripts and debugging traces default to 90-day retention configurable within platform limits. Coordinate deletion of checkpoint history, derived transcript projections, evidence snapshots, vectors, and backups with privacy obligations (Q044, Q058, Q061).

**SEC-008 [OPEN, P0]** Privacy policy, DPA, data residency, GDPR-related obligations, age restrictions, international transfers, and consent requirements; obtain appropriate legal review.

**SEC-009 [OPEN, P0]** Whether customers can request regional processing or opt out of specific model providers.

**SEC-010 [PROPOSED, P0]** Sensitive values shall be redacted from application logs and user-facing error messages.

**SEC-011 [PROPOSED, P0]** Document ownership and deletion requests shall propagate to derived chunks, vectors, and memory artifacts under a documented lifecycle.

---

## 16. Non-functional requirements and service operations

**NFR-001 [PROPOSED, P0]** Define measurable latency targets for widget bootstrap, first streamed token, and full answer, with separate budgets for retrieval and model generation.

**NFR-002 [PROPOSED, P0]** Define availability, backup frequency, recovery point objective (RPO), and recovery time objective (RTO) before production launch.

**NFR-003 [PROPOSED, P0]** Collect structured logs, request IDs, traces, job metrics, database performance metrics, model latency, and cost metrics.

**NFR-004 [PROPOSED, P0]** Support independent scaling of API processes and Celery workers without shared in-memory state assumptions.

**NFR-005 [PROPOSED, P0]** Use connection pooling and bounded concurrency for PostgreSQL, model calls, and background tasks.

**NFR-006 [PROPOSED, P0]** Enforce resource ceilings to prevent a single tenant or document from monopolizing infrastructure.

**NFR-007 [OPEN, P0]** Expected tenants, chatbots, concurrent visitors, documents, and monthly message volume.

**NFR-008 [OPEN, P0]** Hosting region, disaster recovery region, and customer data residency options.

**NFR-009 [PROPOSED, P0]** Provide environment-separated configuration, repeatable migrations, deployment rollback, and production-safe secrets management.

**NFR-010 [CONFIRMED, P0]** Track model/token usage, credit reservation and settlement, and underlying provider costs per organization and chatbot, including embedding work and provider retries (Q059).

---

## 17. Quality assurance and release gates

**QA-001 [PROPOSED, P0]** Unit tests shall cover authorization policies, configuration validation, billing entitlements, usage accounting, and memory-window selection.

**QA-002 [PROPOSED, P0]** Integration tests shall cover PostgreSQL/pgvector, Alembic migrations, LangGraph checkpoint restoration, Celery job execution, and webhook idempotency.

**QA-003 [PROPOSED, P0]** End-to-end tests shall cover organization setup, document upload, ingestion, widget installation, conversation, answer inspection, and subscription state changes.

**QA-004 [PROPOSED, P0]** Security tests shall attempt cross-tenant access via forged IDs, vector filters, thread IDs, widget requests, and trace endpoints.

**QA-005 [PROPOSED, P0]** RAG evaluation fixtures shall include answerable questions, unsupported questions, misleading documents, and multilingual examples when supported.

**QA-006 [PROPOSED, P0]** Long-thread tests shall verify verbatim window preservation, summary updates, checkpoint recovery, and bounded token usage.

**QA-007 [PROPOSED, P0]** Load tests shall measure concurrent visitor requests, embedding workers, database contention, and cost controls.

**QA-008 [OPEN, P0]** Release thresholds for retrieval relevance, groundedness, error rates, latency, and budget adherence.

### MVP release gate

The MVP is not ready for paid production use until tenant isolation, payment verification, quota enforcement, data deletion, checkpoint recovery, background-job reliability, and public-widget abuse protection have passing tests and operational procedures.

---

## 18. Suggested implementation phases (provisional)

### Phase 1 — Application foundation

FastAPI application structure, environment configuration, SQLModel, Alembic, PostgreSQL, organization/auth skeleton, dashboard layout, and testing foundation.

### Phase 2 — Chatbot management

Organization-scoped chatbot CRUD, business rules, domain settings, preview, and authorization.

### Phase 3 — Knowledge ingestion

Object storage, uploads, Celery/Redis, extraction, chunking, embeddings, pgvector, versioning, and progress UI.

### Phase 4 — RAG execution

Tenant-filtered retrieval, LangGraph orchestration, model provider abstraction, grounded responses, and evaluation fixtures.

### Phase 5 — Conversation continuity and inspection

PostgreSQL checkpointer, rolling summaries, verbatim sliding window, transcript archive, trace snapshots, and debugging dashboard.

### Phase 6 — Website widget

Versioned bootstrap script, iframe UI, public chat API, streaming, session management, domain policy, and abuse controls.

### Phase 7 — Billing and entitlements

Payment-provider selection and verification, plans, metering, checkout, webhooks, quotas, and lifecycle handling.

### Phase 8 — Production hardening

Security, privacy workflows, backups, observability, load testing, deployment automation, and controlled launch.

**ROAD-001 [PROPOSED, P0]** Each phase shall produce a testable increment and update implementation status based on the actual GitHub codebase.

**ROAD-002 [CONFIRMED, P0]** Build/test the core product using authorized manually provisioned plans with working entitlements and credit limits. Integrate live payment processing and verified webhooks before accepting paying customers (Q060).

---

## 19. Explicitly deferred candidates

The following are not confirmed MVP commitments:

- **FUT-001 [DEFERRED, P1]:** Website crawling and scheduled knowledge synchronization.
- **FUT-002 [DEFERRED, P1]:** Retrieval experimentation UI and optional dedicated reranking. General-purpose hybrid search with RRF is CONFIRMED for MVP (Q026, Q032).
- **FUT-003 [DEFERRED, P1]:** Human support handoff and ticketing integrations.
- **FUT-004 [DEFERRED, P1]:** Conversation analytics and knowledge-gap reports.
- **FUT-005 [DEFERRED, P1]:** Customer-provided API keys. Centrally managed primary and backup model providers are CONFIRMED (Q028, Q034).
- **FUT-006 [DEFERRED, P2]:** CRM, e-commerce, and external tool integrations.
- **FUT-007 [DEFERRED, P2]:** Autonomous agent workflows and action execution.
- **FUT-008 [DEFERRED, P2]:** Voice, messaging channels, and non-website deployment surfaces.
- **FUT-009 [DEFERRED, P2]:** Regional data residency options and enterprise compliance features.
- **FUT-010 [DEFERRED, P2]:** White-label widget and custom domain support.

---

## 20. Historical provisional question register (superseded)

**Historical note:** The following was an initial provisional topic list, not the actual interactive question IDs. It is retained for historical reference only and must not be used to re-open confirmed Q001–Q061 decisions. For current unresolved requirements, inspect OPEN entries in the specification.

| ID   | Decision                                              | Primary affected sections | Priority |
| ---- | ----------------------------------------------------- | ------------------------- | -------- |
| Q001 | Initial customer segment and primary use case         | 1, 4, 7                   | P0       |
| Q002 | Languages and internationalization/RTL                | 1, 5, 14                  | P0       |
| Q003 | Account registration and authentication methods       | 3                         | P0       |
| Q004 | Organization membership and role permissions          | 3                         | P0       |
| Q005 | Number of chatbots and knowledge-sharing model        | 4, 6                      | P0       |
| Q006 | Rules configuration and publication behavior          | 4                         | P0       |
| Q007 | Widget session identity and persistence               | 5, 8                      | P0       |
| Q008 | Supported upload types, sizes, and quotas             | 6                         | P0       |
| Q009 | Chunking, embeddings, and multilingual retrieval      | 6, 7                      | P0       |
| Q010 | Retrieval strategy and insufficient-evidence behavior | 7                         | P0       |
| Q011 | LLM provider and customer-owned API keys              | 2, 7, 11                  | P0       |
| Q012 | Verbatim window and summary token thresholds          | 8                         | P0       |
| Q013 | Summary timing, concurrency, and failure recovery     | 8                         | P0       |
| Q014 | Transcript and trace retention/redaction              | 8, 9, 15                  | P0       |
| Q015 | Trace inspection granularity and access roles         | 9                         | P0       |
| Q016 | Celery queue/retry and job-state policies             | 10                        | P0       |
| Q017 | Billing provider and Egypt-based payout eligibility   | 11                        | P0       |
| Q018 | Plans, metering units, quotas, and overage            | 11                        | P0       |
| Q019 | Trial, cancellation, failed payments, and refunds     | 11                        | P0       |
| Q020 | Tenant database isolation strategy                    | 3, 12                     | P0       |
| Q021 | Hosting, deployment, and budget                       | 2, 16                     | P0       |
| Q022 | Privacy, data residency, and deletion                 | 15, 16                    | P0       |
| Q023 | Performance, availability, and release targets        | 16, 17                    | P0       |
| Q024 | MVP versus deferred feature boundary                  | 18, 19                    | P0       |
| Q025 | Dashboard/widget branding and UX requirements         | 5, 14                     | P1       |

### Interactive Q&A protocol

1. Present 3–5 decisions per batch with concise trade-offs and a recommended default.
2. Include an **Other** option with a free-text field for every question.
3. Wait for the product owner's selections; do not convert defaults into confirmed decisions automatically.
4. Produce an append-ready Markdown decision report with selected answers, rationale, exact SPEC.md implications, and newly discovered conflicts.
5. Update affected requirement statuses and acceptance criteria after approval.
6. Keep a cumulative decision log and continue to the next unresolved batch.

---

## 21. Decision log

| Date       | Decision                                            | Status    | Notes                                              |
| ---------- | --------------------------------------------------- | --------- | -------------------------------------------------- |
| 2026-11-08 | Product name is **ChatHat**                         | CONFIRMED | Repository: `EslamKamel89/ChatHat`                 |
| 2026-11-08 | GitHub repository is the codebase SSOT              | CONFIRMED | Inspect latest code before implementation guidance |
| 2026-11-08 | FastAPI, SQLModel, Alembic, PostgreSQL, pgvector    | CONFIRMED | Backend and persistence stack                      |
| 2026-11-08 | Jinja2, HTMX, Alpine.js, Tailwind CSS, daisyUI      | CONFIRMED | Dashboard UI stack                                 |
| 2026-11-08 | LangGraph and durable checkpointing                 | CONFIRMED | Prefer supported framework features                |
| 2026-11-08 | Recent verbatim messages plus rolling older summary | CONFIRMED | Exact thresholds remain OPEN                       |
| 2026-11-08 | Celery for background work                          | CONFIRMED | Broker selection remains proposed                  |
| 2026-11-08 | Embedded website chatbot via script tag             | CONFIRMED | Widget implementation details proposed/open        |
| 2026-11-08 | Document upload and configurable business rules     | CONFIRMED | Detailed policies open                             |
| 2026-11-08 | Inspect retrieved context for each answer           | CONFIRMED | Trace schema proposed                              |
| 2026-11-08 | International SaaS billing                          | CONFIRMED | Provider and pricing OPEN                          |
| 2026-11-14 | Feature responsibility subpackages | CONFIRMED | Approved routes, schemas, models, services, dependencies, and feature tests. |
| 2026-11-22 | Responsibility-based test subpackages | CONFIRMED | Mirror feature responsibilities inside `tests/`; keep infrastructure tests grouped under core. |
| 2026-11-11 | Feature-based source organization (TECH-014)       | CONFIRMED | Each feature owns its code and pytest suite.        |

---

## 22. Definition of specification completion

This document becomes an approved implementation baseline when:

1. All P0 OPEN decisions are answered or explicitly deferred with rationale.
2. All P0 PROPOSED requirements are accepted, changed, or rejected.
3. Data ownership, tenant isolation, checkpoint/transcript retention, and billing contracts are internally consistent.
4. Core user journeys have unambiguous acceptance criteria.
5. A minimal launch scope, measurable non-functional targets, and release gates are approved.
6. The approved version is committed to the GitHub repository by an authorized action.

**Current state:** Product decisions Q001–Q061 reconciled; remaining OPEN items still require decisions. No requirements imply that code, tests or infrastructure have been implemented.

---

## 23. Confirmed interactive decisions — Batches 1–11 (Q001–Q055)

This register uses the **interactive Q&A numbering**, which differs from the original provisional question list in section 20. The confirmed choices supersede contradictory earlier OPEN/PROPOSED wording. Detailed decisions Q056–Q061 are in `docs/questions_and_answers.md`; Q001–Q055 are consolidated below.

### Batch 1 — Product identity and accounts

- **Q001:** General-purpose platform with selectable industry templates.
- **Q002:** Fully localized dashboard and chatbot, customer-selected languages and RTL.
- **Q003:** Organization is tenant; creator is owner; invite owners and restricted members.
- **Q004:** Email/password plus Google OAuth.
- **Q005:** Anonymous visitor conversation scoped to browser tab.

### Batch 2 — Organization and configuration

- **Q006:** Each registered user belongs to exactly one organization.
- **Q007:** Custom organization-scoped RBAC.
- **Q008:** Templates copy editable prompts, rules, branding and settings.
- **Q009:** Knowledge bases reusable across chatbots.
- **Q010:** Chatbot Draft/Publish; published config affects new and subsequent existing-conversation messages; traces preserve version.

### Batch 3 — Documents

- **Q011:** Knowledge bases auto-publish after successful ingestion.
- **Q012:** Organization-wide document library; reuse across knowledge bases without duplicate embeddings.
- **Q013:** PDF, DOCX, TXT, Markdown, CSV, XLSX and HTML.
- **Q014:** Skip/report scanned PDF pages; no OCR in MVP.
- **Q015:** Replacement creates a new document; manual deletion of old one.

### Batch 4 — Ingestion and plans

- **Q016:** Confirmed deletion detaches document from all knowledge bases, immediately excludes it from retrieval, then cleans up asynchronously.
- **Q017:** Upload requires selection of one or more knowledge bases.
- **Q018:** Strict all-or-nothing ingestion except Q021 scanned-PDF exception.
- **Q019:** Block exact duplicate uploads within organization.
- **Q020:** Subscription plans govern document count, file size and storage.

### Batch 5 — Failure and history

- **Q021:** Skip unreadable scanned-PDF pages when readable pages exist; all other processing failures are fatal.
- **Q022:** Keep failed uploads/reports; retry idempotently without re-upload.
- **Q023:** On duplicate, show existing document and allow additional knowledge-base attachment.
- **Q024:** Retain historical evidence after document deletion, subject to retention/privacy deletion.
- **Q025:** Block downgrade until customer manually meets destination plan limits.

### Batch 6 — Retrieval and answers

- **Q026:** Template-dependent retrieval; general-purpose uses vector + PostgreSQL full-text hybrid.
- **Q027:** Insufficient evidence: state unavailability and offer configurable support.
- **Q028:** Centrally managed AI models; no customer model selection.
- **Q029:** Latest-message query first; rewrite only when contextually ambiguous.
- **Q030:** No visitor citations; internal evidence available to authorized dashboard users.

### Batch 7 — Retrieval quality and reliability

- **Q031:** Retrieval internals platform-managed, not customer-editable.
- **Q032:** Hybrid ranking uses Reciprocal Rank Fusion.
- **Q033:** Evidence sufficiency uses retrieval signals plus LLM assessment.
- **Q034:** Bounded provider retries, compatible backup provider and trace of all attempts.
- **Q035:** Configurable support links and optional built-in contact form.

### Batch 8 — Conversation state

- **Q036:** Recent verbatim messages plus rolling summary of older messages.
- **Q037:** Configurable verbatim window; merge displaced messages incrementally into previous summary.
- **Q038:** Same-tab refresh restores session; tab closure ends intentional resumability.
- **Q039:** One active response per conversation; disable concurrent sending.
- **Q040:** Authorized users see full transcripts and traces with configurable retention/access.

### Batch 9 — Memory and retention

- **Q041:** Window counts individual user/assistant messages; excludes system/tool messages.
- **Q042:** Maximum summary token budget with compression.
- **Q043:** Summary updates synchronously before answer generation.
- **Q044:** Default transcript/trace retention 90 days, configurable within platform limits.
- **Q045:** Chatbot management permission grants transcript and debugging-trace access.

### Batch 10 — Website widget

- **Q046:** Registered production domains; separate localhost/staging testing mode.
- **Q047:** Advanced branding including fonts, dimensions, launcher icon and message styles.
- **Q048:** JavaScript snippet plus optional inline HTML container.
- **Q049:** Manual availability, business-hours scheduling and offline support.
- **Q050:** Stream responses using SSE.

### Batch 11 — Security and streaming lifecycle

- **Q051:** Exact hostnames and explicitly configured wildcard subdomains.
- **Q052:** Cross-origin iframe controlled by lightweight JavaScript loader.
- **Q053:** Manual forced-online and forced-offline override the schedule until removed; automatic follows schedule.
- **Q054:** Continue server generation after SSE disconnection, persist answer and restore within same tab.
- **Q055:** Layered IP, visitor-session, chatbot and organization rate limits with optional challenges.

### Data-model and lifecycle implications

- Introduce reusable organization-owned knowledge bases and many-to-many `knowledge_base_documents` and `chatbot_knowledge_bases` relationships; exact table design remains provisional.
- Treat industry templates as editable chatbot-configuration snapshots, but keep retrieval pipeline internals centrally managed.
- Separate chatbot Draft/Publish from knowledge-base auto-publication.
- Persist ingestion attempts, source-file digests, failure reports and publication state; enforce retrieval exclusion before deletion cleanup.
- Persist immutable answer evidence and effective configuration version, subject to privacy and retention policies.
- Keep full original message history authoritative in LangGraph checkpoint state; model-input summaries and dashboard transcripts are derived, with a persisted summary cursor and serialized state updates.
- Model availability as automatic / forced online / forced offline rather than one boolean.
- Persist generation independently of SSE transport and deduplicate reconnection/replay.
- Enforce domain checks, authorization and layered abuse limits server-side.

### Unresolved details — do not infer

- Initial supported language catalog and locale fallback.
- Industry-specific retrieval pipelines, RRF parameters, ambiguity detection and evidence thresholds.
- Model/embedding providers, fallback compatibility, timeout budgets and exact credit settlement for failed/retried operations.
- Summary token limits, tool-message context handling, checkpoint performance, transaction boundaries and crash recovery; full original history must remain recoverable.
- Retention range, cleanup schedule, backup deletion and privacy/legal obligations.
- Contact form fields, storage, delivery, consent and spam protection.
- Wildcard syntax, test-mode restrictions, iframe postMessage/CSP contracts.
- Time zones, holiday schedules, overnight hours and active-stream availability changes.
- SSE deadline, reconnect credentials, result recovery and usage charging.
- Rate-limit thresholds, challenges and distributed counter storage.
- Whether chatbot management permission grants access across every chatbot or a narrower scope.

### Change log

| Date       | Version | Change                                                                                                                                                                         |
| ---------- | ------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 2026-11-22 | 0.4.3 | Require responsibility-based test subpackages within each feature; align authentication examples and preserve the standard container pytest trigger. |
| 2026-11-17 | 0.4.2 | Require directory-only core and feature roots with `__init__.py` as the sole file exception; align lifespan and settings locations with responsibility subdirectories. |
| 2026-11-08 | 0.2.0   | Reconciled confirmed interactive decisions Q001–Q055 across requirement definitions, memory lifecycle, deferred features and decision register.                                |
| 2026-11-08 | 0.3.0   | Incorporated Q056–Q061: shared-table tenancy, canonical embeddings, checkpoint-authoritative full history, monthly AI credits, manual test plans and paid-launch payment gate. |
| 2026-11-14 | 0.4.1 | Recorded the approved feature subpackages and authentication target layout. |
| 2026-11-11 | 0.4.0   | Added TECH-014 for feature packages that own their code and pytest suites. |

---

## 24. Confirmed architectural decisions — Batch 12 and Q061 (Q056–Q061)

These choices are confirmed product-owner decisions, not proof of implementation. Full decision rationale is in `docs/questions_and_answers.md`.

### Q056 — Shared-table tenant isolation

One shared PostgreSQL database with shared tables. Every organization-owned resource must be scoped and authorized by its organization; client-provided tenant IDs are untrusted. This includes relational reads/writes, canonical embeddings, LangGraph checkpoints, traces, and credit accounting. Application-level authorization is mandatory; PostgreSQL RLS remains optional defense in depth.

### Q057 — Canonical document embeddings

Generate one canonical chunk/embedding representation per document and embedding-model version. Knowledge bases refer to shared document chunks, and chatbots retrieve only through their attached knowledge bases. Reuse does not duplicate embeddings. Global deletion removes retrieval eligibility across all knowledge bases before asynchronous physical cleanup; detachment from one knowledge base does not delete embeddings needed elsewhere.

### Q058 — LangGraph checkpoints as sole conversation authority

Durable LangGraph checkpoint state is the sole authority for conversation history and response state. Dashboard transcripts and model-input context are derived, not independently authoritative. This does **not** make checkpoints authoritative for unrelated domain data such as credit balances, billing records, uploaded documents, or platform audit events.

### Q059 — Monthly AI credits

Plans allocate monthly AI credits. Chargeable operations reserve available credits before execution, then settle measured model/token usage with an idempotent ledger. Unused reservations are released. Exact conversion rates, allowances, overage policy, and retry/failure settlement are still OPEN; do not invent them. The ledger is an authoritative financial/entitlement record, separate from conversation history.

### Q060 — Manual plans during core development

Build and test with securely administered manually provisioned plans. Entitlement checks and credit accounting must work without a payment provider. Select and integrate a live payment provider, checkout and verified webhooks before accepting paying customers. The provider selection itself is deferred until that phase.

### Q061 — Full original messages retained in checkpoint state

**Clarification of Q058:** Keep complete original user/assistant message history durably recoverable from LangGraph checkpoint state for the applicable retention period. Construct a bounded rolling summary plus recent verbatim window solely for LLM input. Summarization must never overwrite or delete original history. Dashboard transcripts are derived from checkpoints; optional read projections are rebuildable and never independent authorities.

The persisted summary cursor must identify exactly which original messages were summarized. Before generating a new answer, update summary/cursor consistently. One active operation per conversation, idempotent completion, and checkpoint recovery are required. SSE disconnect does not stop server-side generation; the completed response is checkpointed once and recoverable within the same tab session.

**Engineering verification required before conversation implementation:** Confirm the selected LangGraph checkpointer supports complete original-history persistence/reconstruction and the required retention/deletion behavior. Measure long-conversation checkpoint growth, serialization cost, crash recovery, and read-projection rebuild performance. External provider calls, SSE delivery, and credit-ledger transactions must not be assumed atomic with checkpoint writes.

### Acceptance criteria for Q056–Q061

1. Forged organization, knowledge-base, document, or checkpoint identifiers cannot reveal another tenant's data.
2. Attaching the same document to another knowledge base does not regenerate identical embeddings; retrieval membership remains enforced.
3. A long conversation can produce a complete verbatim transcript from checkpoint state after summaries have been compressed multiple times.
4. Repeating a request or reconnecting after SSE disconnection does not create duplicate assistant messages or duplicate charges.
5. Concurrent credit reservations cannot exceed the organization's available credit balance; final charges reconcile measured usage.
6. An authorized operator can provision a test plan without live payments, while ordinary organization users cannot grant themselves credits.
7. Paid customers cannot be onboarded until payment-provider integration and verified webhook processing are ready.

### Remaining high-impact implementation contracts (not new product decisions)

- Verify checkpoint durability, full-history reconstruction, storage growth, idempotent response completion, and cleanup before building conversation persistence.
- Design credit reservation/settlement/release with concurrency control, accounting for provider retries and interrupted streams.
- Define database constraints and tenant-scoping patterns before writing tenant-owned models.
- Choose embedding model and version migration strategy when implementing ingestion.
- Choose live payment provider before the first paid launch, not before initial core development.

## 24. Docker Compose — Development and Production Infrastructure

**Decision ID:** INFRA-001  
**Status:** CONFIRMED  
**Priority:** P0  
**Date:** 2026-11-08

### 24.1 Core Decision

ChatHat shall use **Docker and Docker Compose for both local development and production deployment**.

Docker Compose shall be the primary mechanism for defining, configuring, starting, and managing the application's services in both environments.

The development and production environments shall share the same fundamental service architecture while allowing environment-specific configuration.

Kubernetes and other container orchestration platforms are not required for the initial release.

### 24.2 Service Architecture

**INFRA-006 [CONFIRMED, P0] — Nginx Reverse Proxy**

ChatHat shall use **Nginx as a dedicated Docker Compose service** in both development and production environments.

The Docker Compose architecture shall support the following services:

| Service               | Responsibility                                                                                        |
| --------------------- | ----------------------------------------------------------------------------------------------------- |
| Nginx                 | Reverse proxy, HTTP routing, static assets, SSE proxy configuration, and production HTTPS termination |
| FastAPI               | HTTP API, dashboard, authentication, chatbot endpoints, and SSE streaming                             |
| PostgreSQL + pgvector | Application database, vector embeddings, and LangGraph checkpoints                                    |
| Redis                 | Celery message broker and approved shared-state requirements                                          |
| Celery Worker         | Document ingestion, embedding generation, and asynchronous background tasks                           |
| Celery Beat           | Scheduled maintenance, retention cleanup, and periodic tasks when required                            |

#### Nginx Requirements

1. Nginx shall run in its own container and communicate with FastAPI over the internal Docker Compose network.
2. Nginx shall serve as the public entry point for application HTTP traffic.
3. Production Nginx shall terminate HTTPS using valid TLS certificates.
4. Nginx shall forward the appropriate client IP, host, and protocol information to FastAPI using trusted proxy headers.
5. Nginx shall support long-lived SSE connections by disabling response buffering for streaming endpoints and configuring appropriate timeouts.
6. Nginx shall enforce appropriate request body size limits, particularly for document uploads.
7. Nginx shall serve static assets directly where practical.
8. PostgreSQL, Redis, Celery, and FastAPI shall not expose public ports in production.
9. Development Nginx may use HTTP, while production shall enforce HTTPS.
10. Nginx configuration shall be version-controlled, with environment-specific settings where necessary.

#### Expected Request Flow

```text
Website Visitor / Dashboard User
              |
              v
          Nginx
       (Docker Service)
              |
              v
          FastAPI
              |
       +------+------+
       |             |
       v             v
   PostgreSQL      Redis
   + pgvector        |
                     v
                Celery Worker
```

**Acceptance criteria:** All public HTTP requests pass through Nginx; SSE streams function without proxy buffering; internal infrastructure services remain inaccessible from the public internet.

### 24.3 Development Environment

**INFRA-002 [CONFIRMED, P0]**

The local development environment shall:

1. Start required infrastructure and application services through Docker Compose.
2. Support source-code bind mounts and FastAPI automatic reload for efficient development.
3. Use persistent Docker volumes for PostgreSQL data and other state that must survive container restarts.
4. Load development configuration from environment variables and development-specific configuration files.
5. Support running Alembic migrations, management commands, and pytest inside containers.
6. Expose only the ports needed for local development and debugging.
7. Allow developers to inspect logs, restart services, and execute commands using standard Docker Compose commands.
8. Avoid requiring PostgreSQL, Redis, or other infrastructure services to be installed directly on the host operating system.

### 24.4 Production Environment

**INFRA-003 [CONFIRMED, P0]**

The production environment shall:

1. Deploy application services using Docker Compose.
2. Use production-ready container images without development bind mounts or automatic reload.
3. Support configurable FastAPI and Celery process concurrency.
4. Persist PostgreSQL data using appropriate durable storage.
5. Keep PostgreSQL, Redis, and internal service ports inaccessible from the public internet.
6. Expose public application traffic through a reverse proxy with HTTPS.
7. Manage production secrets securely without embedding credentials in Docker images or committing them to Git.
8. Define health checks, restart policies, and appropriate resource limits.
9. Support database migrations as an explicit deployment step.
10. Support repeatable deployment and rollback procedures.
11. Implement automated backups and periodically verify restoration.
12. Support monitoring, centralized or persistent logs, and operational diagnostics.

Docker Compose restart policies and health checks do not, by themselves, provide high availability or automatic failover. Production availability and recovery requirements must be addressed separately.

### 24.5 Configuration Strategy

**INFRA-004 [CONFIRMED, P0]**

ChatHat shall maintain a shared Compose configuration with environment-specific overrides or equivalent Compose configuration files.

The implementation should follow this structure unless a simpler maintainable arrangement is justified:

```text
ChatHat/
├── Dockerfile
├── compose.yaml
├── compose.dev.yaml
├── compose.prod.yaml
├── .env.example
├── .dockerignore
└── ...
```

- `compose.yaml` defines shared service configuration.
- `compose.dev.yaml` defines development-specific behavior.
- `compose.prod.yaml` defines production-specific behavior.
- `.env.example` documents required configuration variables without exposing secrets.
- `Dockerfile` defines the application image build.

Development and production should use compatible application images and dependency versions to reduce environment-specific failures.

### 24.6 Testing Requirements

**INFRA-005 [CONFIRMED, P0]**

The testing strategy shall integrate with Docker Compose and pytest.

1. Tests must be executable inside the application container.
2. Integration tests shall run against isolated PostgreSQL and Redis test resources when required.
3. Database tests must never modify development or production data.
4. Test database initialization and Alembic migrations must be reproducible.
5. Integration tests shall verify real infrastructure behavior rather than relying exclusively on mocks.
6. CI shall execute relevant tests using a reproducible container-based environment.
7. Container startup, health checks, and service connectivity shall be verified before production deployment.

### 24.7 Implementation Plan Impact

The implementation curriculum shall introduce Docker Compose in **Phase 01**, not postpone containerization until deployment.

The recommended progression is:

1. Create the application Dockerfile and development Compose configuration.
2. Run FastAPI inside Docker with automatic reload.
3. Introduce PostgreSQL and pgvector through Compose.
4. Configure Alembic migrations and isolated pytest database execution.
5. Introduce Redis and Celery when asynchronous processing is implemented.
6. Add production Compose configuration, reverse proxy, secrets handling, health checks, backups, and deployment procedures.
7. Verify production behavior through deployment and recovery tests.

All subsequent implementation and testing lessons shall use the Docker Compose development environment as their standard execution environment.

### 24.8 Acceptance Criteria

This decision is implemented when:

- A developer can clone the repository, configure the required environment variables, and start the application using Docker Compose.
- FastAPI, PostgreSQL, Redis, and Celery operate together when their respective phases are implemented.
- pytest and Alembic commands run successfully within the containerized development environment.
- Production deployment uses Docker Compose with production-specific configuration.
- Application and database state survive ordinary container restarts.
- Production services are appropriately isolated, secured, monitored, and backed up.
- Development and production deployment procedures are documented and reproducible.

### 24.9 Related Specification Requirements

This decision refines the following existing requirements:

- `TECH-008` — Redis and Celery infrastructure.
- `TECH-010` — Modular monolith with separately deployable processes.
- `TECH-013` — Deployment topology.
- `JOB-002` — Background workers.
- `NFR-002` — Availability, backups, and recovery.
- `NFR-004` — API and worker scaling.
- `NFR-009` — Environment configuration and deployment.
- `QA-002` — Infrastructure integration testing.
- `ROAD-001` — Incremental implementation phases.

**Remaining decisions:** Production hosting provider, server sizing, deployment region, backup targets, and availability objectives remain open. Docker Compose does not determine these choices.
