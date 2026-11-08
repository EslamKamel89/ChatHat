# ChatHat — Product Requirements Specification

> **Document version:** 0.2.0  
> **Status:** Draft — decisions Q001–Q055 incorporated; unresolved implementation details remain  
> **Last updated:** 2026-11-08  
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

### 2.1 Engineering principles
- Preserve explicit boundaries between HTTP/API, business services, persistence, AI orchestration, background tasks, and third-party providers.
- Prefer small, testable modules over premature microservices.
- Use LangGraph for checkpointing, graph execution, and applicable memory tools; custom code is justified for product-specific contracts, audit records, tenant isolation, and retrieval diagnostics.
- Separate product requirements from specific library APIs. Verify current LangGraph recommendations at implementation time; do not assume that a particular agent or middleware API remains unchanged.
- Treat browser-provided chatbot IDs, thread IDs, and metadata as untrusted input.

---

## 3. Organizations, authentication, and authorization

**AUTH-001 [PROPOSED, P0]** The dashboard shall require authenticated users.

**AUTH-002 [PROPOSED, P0]** Every organization-owned resource shall be scoped by organization identity and permissions.

**AUTH-003 [PROPOSED, P0]** A chatbot shall belong to exactly one organization at a time.

**AUTH-004 [PROPOSED, P0]** Server-side authorization shall protect all organization, document, conversation, trace, and billing endpoints; hiding controls in the UI is insufficient.

**AUTH-005 [PROPOSED, P0]** The platform shall enforce isolation during retrieval, including vector search filters, not just when rendering results.

**AUTH-006 [CONFIRMED, P0]** Support email/password and Google OAuth; verification, recovery and account-linking policies remain OPEN.

**AUTH-007 [CONFIRMED, P0]** Organization owners invite users and assign custom roles; chatbot management permission grants access to conversation transcripts and traces. Scope across chatbots remains OPEN.

**AUTH-008 [PROPOSED, P1]** Consider PostgreSQL row-level security as defense in depth after application-level tenant scoping is established and tested.

**AUTH-009 [PROPOSED, P0]** Administrative actions affecting access, billing, and data deletion shall generate audit events.

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

**WID-007 [CONFIRMED, P0]** Stream responses using SSE; browser disconnection does not cancel server generation, and completed answers are persisted once and recoverable within the same tab session.

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

**DOC-007 [CONFIRMED, P0]** Documents belong to an organization-wide library and are reusable across knowledge bases without duplicate uploads or embeddings; chunks retain tenant and source metadata.

**DOC-008 [CONFIRMED, P0]** Knowledge bases auto-publish successful ingestion for the next chatbot message. Ingestion is atomic except unreadable scanned-PDF pages may be skipped and reported when readable pages exist.

**DOC-009 [CONFIRMED, P0]** Retain failed source uploads and reports for authorized idempotent retries with attempt history. Block exact duplicate uploads within an organization; permit attaching an existing document to additional knowledge bases.

**DOC-010 [CONFIRMED, P0]** Replacement creates a new document; the owner deletes the old one manually. Confirmed deletion detaches all knowledge bases, excludes chunks from retrieval immediately and cleans them asynchronously; historical evidence remains subject to retention.

**DOC-011 [CONFIRMED, P0]** Document counts, individual file size, storage and related limits depend on subscription plan; numerical values remain OPEN.

**DOC-012 [CONFIRMED, P1]** Skip and report unreadable scanned-PDF pages without OCR; PDFs with zero readable text cannot publish. Other ingestion sources remain OPEN or DEFERRED.

**DOC-013 [OPEN, P0]** Chunking method, chunk sizes, embedding dimensionality, re-embedding/version migration, and multilingual handling.

**DOC-014 [PROPOSED, P0]** Uploads shall be checked for permitted type, content/size limits, path safety, and malicious content risks; parsers shall run with constrained resources.

### Acceptance criteria
- A valid file progresses from uploaded to ready, and its chunks are retrievable only for authorized chatbots.
- An invalid or unsupported file fails clearly without leaving partially published knowledge.
- A failed Celery task can be retried without duplicate searchable chunks.
- A document replacement does not expose an incomplete mixture of old and new chunks.

---

## 7. RAG retrieval and grounded generation

**RAG-001 [CONFIRMED, P0]** Retrieval is centrally managed by industry template; general-purpose retrieval combines pgvector similarity and PostgreSQL full-text search using Reciprocal Rank Fusion (RRF).

**RAG-002 [PROPOSED, P0]** Retrieval shall enforce tenant and chatbot authorization filters before evidence is used for generation.

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

**MEM-002 [CONFIRMED, P0]** Conversation state shall use durable checkpointing.

**MEM-003 [CONFIRMED, P0]** The LLM shall receive a sliding window of recent conversation messages verbatim, plus a rolling summary of older messages.

**MEM-004 [CONFIRMED, P0]** The configurable verbatim window counts individual user and assistant messages, excluding system/tool messages; displaced messages are incrementally summarized, with summary token limits and compression.

**MEM-005 [PROPOSED, P0]** A conversation thread shall be bound server-side to its chatbot and tenant; clients may not use arbitrary thread IDs to access other conversations.

**MEM-006 [PROPOSED, P0]** Model context shall be assembled from trusted system rules, rolling summary, recent verbatim messages, retrieved evidence, and the current user request, without unintentionally duplicating the current message.

**MEM-007 [CONFIRMED, P0]** Keep complete original transcripts separately from rolling summaries and LangGraph checkpoint state.

**MEM-008 [CONFIRMED, P0]** Merge displaced messages into the previous summary exactly once using a persisted cursor; preserve recent verbatim messages and never advance the cursor after failed summarization.

**MEM-009 [CONFIRMED, P0]** Only one response-generation operation may run per conversation; the widget disables additional sends and the server enforces concurrency protection.

**MEM-010 [CONFIRMED, P0]** Update the rolling summary synchronously in the active conversation request before generating the next answer.

**MEM-011 [CONFIRMED, P0]** Retain full transcripts and debugging traces for 90 days by default; organizations may configure retention within platform limits. Other data-category retention remains OPEN.

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

**DBG-002 [PROPOSED, P0]** A trace shall link organization, chatbot, conversation, visitor message, assistant response, and execution identifier.

**DBG-003 [CONFIRMED, P0]** Trace original/rewritten queries, branch and fused retrieval ranks, evidence sufficiency, source snapshots, effective configuration, model/provider, retries/failover, latency, errors and usage.

**DBG-004 [PROPOSED, P0]** A trace shall distinguish retrieved candidate chunks from chunks actually passed to the LLM after filtering or truncation.

**DBG-005 [PROPOSED, P0]** Authorized users shall inspect effective model context or a privacy-safe representation; secrets and internal credentials must never appear in traces.

**DBG-006 [PROPOSED, P0]** Logs and traces shall use correlation IDs across FastAPI, LangGraph, Celery, and database operations.

**DBG-007 [OPEN, P0]** Whether to retain full prompts/model outputs, redact sensitive data, or use configurable trace levels.

**DBG-008 [OPEN, P1]** Answer feedback, evaluation datasets, regression tests, analytics dashboards, and automatic quality scoring.

**DBG-009 [CONFIRMED, P0]** Retain traces for 90 days by default with organization-configurable periods within platform limits; source deletion does not erase retained evidence snapshots, subject to privacy deletion.

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

**BILL-003 [PROPOSED, P0]** Billing shall be isolated behind a provider adapter, keeping internal subscription/entitlement logic independent of a specific payment API.

**BILL-004 [PROPOSED, P0]** Subscription state shall be synchronized from verified, idempotently processed provider webhooks.

**BILL-005 [CONFIRMED, P0]** Plan limits cover chatbots, documents, individual file size, storage and AI usage; block downgrades until the customer manually reduces usage, without automatic deletion.

**BILL-006 [OPEN, P0]** Pricing model: subscription-only, included usage with overage, prepaid credits, or hybrid; currencies and tax-inclusive display.

**BILL-007 [OPEN, P0]** Metering unit: messages, tokens, model cost, or credits; define whether failed requests and retries consume allowance.

**BILL-008 [PROPOSED, P0]** Quotas shall be checked server-side before expensive model work and updated using concurrency-safe accounting.

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

| Entity | Key responsibilities | Decision status |
|---|---|---|
| `organizations` | Tenant identity, settings, lifecycle | PROPOSED |
| `users` | Dashboard identities | PROPOSED |
| `memberships` | User-to-organization roles | PROPOSED |
| `chatbots` | Public chatbot identity and configuration | PROPOSED |
| `chatbot_domains` | Allowed host origins/domains | PROPOSED |
| `documents` | Source file metadata and ownership | PROPOSED |
| `document_versions` | Revisions and publication status | PROPOSED |
| `document_chunks` | Chunk text, metadata, vectors | PROPOSED |
| `ingestion_jobs` | Background progress and errors | PROPOSED |
| `visitor_sessions` | Anonymous/session identity | OPEN |
| `conversations` | Tenant/chatbot/thread binding | PROPOSED |
| `conversation_messages` | Verbatim transcript archive | PROPOSED |
| `answer_traces` | Execution and model metadata | PROPOSED |
| `retrieval_trace_chunks` | Ranked retrieved evidence snapshots | PROPOSED |
| `plans` | Plan definitions and limits | PROPOSED |
| `subscriptions` | Provider-linked subscription state | PROPOSED |
| `usage_events` | Idempotent metering ledger | PROPOSED |
| `billing_webhook_events` | Deduplicated provider event processing | PROPOSED |
| `audit_events` | Sensitive configuration/access changes | PROPOSED |
| LangGraph checkpoint tables | Durable thread/graph state, framework-owned | CONFIRMED need; schema framework-managed |

**DATA-001 [PROPOSED, P0]** All tenant-owned entities shall carry an enforceable tenant relationship, directly or through a securely validated parent.

**DATA-002 [PROPOSED, P0]** Database migrations for ChatHat-owned tables shall be managed through Alembic.

**DATA-003 [PROPOSED, P0]** LangGraph-owned persistence tables shall follow the supported checkpointer's setup and schema-management contract, not be manually recreated as SQLModel entities.

**DATA-004 [PROPOSED, P0]** Document/chunk records shall support safe version replacement and cleanup.

**DATA-005 [PROPOSED, P0]** Usage accounting shall be idempotent and reconcilable to model/provider consumption.

**DATA-006 [OPEN, P0]** Shared tables versus database-per-tenant; initial recommendation is shared PostgreSQL with strict scoping.

**DATA-007 [OPEN, P0]** Vector indexing strategy and filtering/index performance as tenant and document counts grow.

---

## 13. API and interface contracts

These are conceptual endpoint groups, **not finalized routes**.

| Interface | Responsibilities |
|---|---|
| Auth/session | Sign in, sign out, verification, account recovery |
| Organization | Organization profile, members, permissions |
| Chatbot management | CRUD, configuration, preview, publish/disable |
| Knowledge | Upload, list, replace, delete, ingestion status |
| Public widget | Bootstrap/config, visitor session, chat streaming |
| Conversations | List, view messages, search/filter |
| Answer inspection | Trace metadata, retrieved evidence, model context |
| Billing | Checkout/session, plan changes, subscription status |
| Provider webhooks | Verified, idempotent payment event intake |
| Operations | Health, readiness, monitoring, administrative tools |

**API-001 [PROPOSED, P0]** Dashboard endpoints shall enforce authenticated tenant authorization.

**API-002 [PROPOSED, P0]** Public widget endpoints shall expose only public configuration and permitted chat operations.

**API-003 [CONFIRMED, P0]** Define SSE partial/completed/error states and recovery of server-completed responses after browser disconnect without duplicate generation.

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

**SEC-001 [PROPOSED, P0]** Apply tenant authorization consistently to relational queries, vector retrieval, checkpoint/thread access, and traces.

**SEC-002 [PROPOSED, P0]** Store provider API keys and other credentials server-side using appropriate secret management; never expose them to widget visitors.

**SEC-003 [PROPOSED, P0]** Enforce TLS, secure session cookies, CSRF protections for cookie-authenticated state changes, and relevant browser security headers.

**SEC-004 [PROPOSED, P0]** Validate uploads, constrain document parsing, and prevent file-path traversal and unauthorized file access.

**SEC-005 [CONFIRMED, P0]** Apply layered IP/session/chatbot/organization rate limits, optional challenges, domain restrictions and cost ceilings.

**SEC-006 [PROPOSED, P0]** Treat retrieved content, document text, and visitor prompts as untrusted with respect to platform instructions and tool permissions.

**SEC-007 [CONFIRMED, P0]** Transcripts and traces default to 90-day retention configurable within platform limits; source deletion removes searchable chunks while preserving historical evidence until expiry or applicable privacy deletion.

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

**NFR-010 [PROPOSED, P0]** Define cost telemetry per organization and chatbot, including embeddings, LLM calls, storage, and background processing.

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

**ROAD-002 [OPEN, P0]** Whether billing must be implemented before public beta access; recommended before accepting paying customers.

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

## 20. Open-decision register for interactive Q&A

These questions should be resolved in small batches. Each selected answer must update the corresponding requirement IDs and any dependent acceptance criteria.

| ID | Decision | Primary affected sections | Priority |
|---|---|---|---|
| Q001 | Initial customer segment and primary use case | 1, 4, 7 | P0 |
| Q002 | Languages and internationalization/RTL | 1, 5, 14 | P0 |
| Q003 | Account registration and authentication methods | 3 | P0 |
| Q004 | Organization membership and role permissions | 3 | P0 |
| Q005 | Number of chatbots and knowledge-sharing model | 4, 6 | P0 |
| Q006 | Rules configuration and publication behavior | 4 | P0 |
| Q007 | Widget session identity and persistence | 5, 8 | P0 |
| Q008 | Supported upload types, sizes, and quotas | 6 | P0 |
| Q009 | Chunking, embeddings, and multilingual retrieval | 6, 7 | P0 |
| Q010 | Retrieval strategy and insufficient-evidence behavior | 7 | P0 |
| Q011 | LLM provider and customer-owned API keys | 2, 7, 11 | P0 |
| Q012 | Verbatim window and summary token thresholds | 8 | P0 |
| Q013 | Summary timing, concurrency, and failure recovery | 8 | P0 |
| Q014 | Transcript and trace retention/redaction | 8, 9, 15 | P0 |
| Q015 | Trace inspection granularity and access roles | 9 | P0 |
| Q016 | Celery queue/retry and job-state policies | 10 | P0 |
| Q017 | Billing provider and Egypt-based payout eligibility | 11 | P0 |
| Q018 | Plans, metering units, quotas, and overage | 11 | P0 |
| Q019 | Trial, cancellation, failed payments, and refunds | 11 | P0 |
| Q020 | Tenant database isolation strategy | 3, 12 | P0 |
| Q021 | Hosting, deployment, and budget | 2, 16 | P0 |
| Q022 | Privacy, data residency, and deletion | 15, 16 | P0 |
| Q023 | Performance, availability, and release targets | 16, 17 | P0 |
| Q024 | MVP versus deferred feature boundary | 18, 19 | P0 |
| Q025 | Dashboard/widget branding and UX requirements | 5, 14 | P1 |

### Interactive Q&A protocol
1. Present 3–5 decisions per batch with concise trade-offs and a recommended default.
2. Include an **Other** option with a free-text field for every question.
3. Wait for the product owner's selections; do not convert defaults into confirmed decisions automatically.
4. Produce an append-ready Markdown decision report with selected answers, rationale, exact SPEC.md implications, and newly discovered conflicts.
5. Update affected requirement statuses and acceptance criteria after approval.
6. Keep a cumulative decision log and continue to the next unresolved batch.

---

## 21. Decision log

| Date | Decision | Status | Notes |
|---|---|---|---|
| 2026-11-08 | Product name is **ChatHat** | CONFIRMED | Repository: `EslamKamel89/ChatHat` |
| 2026-11-08 | GitHub repository is the codebase SSOT | CONFIRMED | Inspect latest code before implementation guidance |
| 2026-11-08 | FastAPI, SQLModel, Alembic, PostgreSQL, pgvector | CONFIRMED | Backend and persistence stack |
| 2026-11-08 | Jinja2, HTMX, Alpine.js, Tailwind CSS, daisyUI | CONFIRMED | Dashboard UI stack |
| 2026-11-08 | LangGraph and durable checkpointing | CONFIRMED | Prefer supported framework features |
| 2026-11-08 | Recent verbatim messages plus rolling older summary | CONFIRMED | Exact thresholds remain OPEN |
| 2026-11-08 | Celery for background work | CONFIRMED | Broker selection remains proposed |
| 2026-11-08 | Embedded website chatbot via script tag | CONFIRMED | Widget implementation details proposed/open |
| 2026-11-08 | Document upload and configurable business rules | CONFIRMED | Detailed policies open |
| 2026-11-08 | Inspect retrieved context for each answer | CONFIRMED | Trace schema proposed |
| 2026-11-08 | International SaaS billing | CONFIRMED | Provider and pricing OPEN |

---

## 22. Definition of specification completion

This document becomes an approved implementation baseline when:

1. All P0 OPEN decisions are answered or explicitly deferred with rationale.
2. All P0 PROPOSED requirements are accepted, changed, or rejected.
3. Data ownership, tenant isolation, checkpoint/transcript retention, and billing contracts are internally consistent.
4. Core user journeys have unambiguous acceptance criteria.
5. A minimal launch scope, measurable non-functional targets, and release gates are approved.
6. The approved version is committed to the GitHub repository by an authorized action.

**Current state:** Product decisions Q001–Q055 reconciled; remaining OPEN items still require decisions. No requirements imply that code, tests or infrastructure have been implemented.

---

## 23. Confirmed interactive decisions — Batches 1–11 (Q001–Q055)

This register uses the **interactive Q&A numbering**, which differs from the original provisional question list in section 20. The confirmed choices below supersede contradictory earlier OPEN/PROPOSED wording. Full decision explanations for Q001–Q050 are in `docs/questions_and_answers.md`; Q051–Q055 were confirmed on 2026-11-08 and should be appended to that file separately.

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
- Keep full transcripts separate from compacted LangGraph memory, with a persisted summary cursor and serialized state updates.
- Model availability as automatic / forced online / forced offline rather than one boolean.
- Persist generation independently of SSE transport and deduplicate reconnection/replay.
- Enforce domain checks, authorization and layered abuse limits server-side.

### Unresolved details — do not infer

- Initial supported language catalog and locale fallback.
- Industry-specific retrieval pipelines, RRF parameters, ambiguity detection and evidence thresholds.
- Model/embedding providers, fallback compatibility, timeout budgets and failed-request billing.
- Summary token limits, tool-message context handling, checkpoint consistency and recovery.
- Retention range, cleanup schedule, backup deletion and privacy/legal obligations.
- Contact form fields, storage, delivery, consent and spam protection.
- Wildcard syntax, test-mode restrictions, iframe postMessage/CSP contracts.
- Time zones, holiday schedules, overnight hours and active-stream availability changes.
- SSE deadline, reconnect credentials, result recovery and usage charging.
- Rate-limit thresholds, challenges and distributed counter storage.
- Whether chatbot management permission grants access across every chatbot or a narrower scope.

### Change log

| Date | Version | Change |
|---|---|---|
| 2026-11-08 | 0.2.0 | Reconciled confirmed interactive decisions Q001–Q055 across requirement definitions, memory lifecycle, deferred features and decision register. |
