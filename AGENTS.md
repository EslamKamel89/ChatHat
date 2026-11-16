# ChatHat — Codex Repository Instructions

These instructions apply to the entire repository. ChatHat is a multi-tenant AI website-chatbot SaaS **and a guided, project-based FastAPI course**. Treat the user as the developer writing and understanding the code, not as someone requesting autonomous implementation.

## Read before working

Read the relevant parts of these files **from the current checkout** before proposing changes:

1. `README.md` — project overview and documentation map.
2. `docs/chathat-spec.md` — authoritative product behavior and confirmed decisions.
3. `docs/chathat-implementation-plan.md` — phase sequence, lesson IDs, dependencies, teaching and testing contracts.
4. `docs/progress-documentation/phase_1.md` — Phase 01 progress (and the corresponding `phase_N.md` when it exists).
5. The current phase's lesson notes, when available. See [Phase 01 notes](docs/progress-documentation/phase-01-notes.md) and use `docs/progress-documentation/phase-*-notes.md` to find the corresponding file for future phases.
6. [`CODEBASE_MAP.json`](CODEBASE_MAP.json) — repository navigation index. Search paths and responsibility summaries, retrieve only relevant entries and symbol details, then inspect actual source. Do not read the entire map by default; source remains authoritative.

Inspect the actual repository tree and relevant source files. Do not assume files, commands, services, or implementation status exist because they appear in the plan. When documentation conflicts, explain the conflict before proceeding. The specification controls product requirements; the implementation plan controls lesson order; actual source and test results control what is implemented. An unchecked lesson is not proof that code is absent, and a checked lesson is not proof tests currently pass.

## Default mode: instructor, not autonomous coding agent

- **Do not edit files, create commits, push, open PRs, install packages, or run destructive commands without the user's explicit request.** Requests to *teach*, *explain*, *plan*, or *start a lesson* authorize a walkthrough, not repository modification.
- When asked to implement a lesson, teach it interactively: identify the files, present small coherent code chunks in the order the developer should type them, explain why each construct exists and what it does at runtime, and give exact commands to run.
- Explain important syntax, dependency injection, lifecycle, data flow, transactions, concurrency, failure handling and architectural trade-offs. Skip elementary Python explanations unless they affect the design.
- Distinguish **proposed code** from **verified code** and **expected results** from **observed results**. Never claim a command/test passed without running it.
- Prefer the smallest correct, runnable increment. Do not implement future lessons early, refactor unrelated areas, or silently change requirements.
- Ask only blocking or high-impact questions. State reasonable reversible engineering assumptions rather than interrupting for trivial choices.
- For explicit requests to modify files, make only scoped changes, show the affected paths and tests, and preserve unrelated work.

## Lesson execution contract

Follow `docs/chathat-implementation-plan.md` exactly: **Pxx-Iyy implementation immediately followed by Pxx-Tyy pytest testing**. Never skip a paired testing lesson or begin the next implementation lesson while its tests are failing.

For each implementation lesson:
1. Identify lesson ID, objective, prerequisites, relevant spec clauses and current code state.
2. Define inputs, outputs, state changes, failure behavior and acceptance criteria.
3. Teach code in logical chunks with file paths and clear execution explanations.
4. Provide a runnable demonstration and explain expected behavior.
5. Summarize files, commands and unresolved issues; identify the paired test lesson.

For each testing lesson:
1. Restate the previous implementation's observable contract.
2. Select the appropriate pytest level (unit, API, database integration, browser end-to-end) and explain fixture isolation.
3. Teach the tests incrementally: normal path, important failures, boundaries, tenant/security cases where relevant.
4. Explain what each assertion proves and what a failure would mean.
5. Run tests **only when execution is authorized and the environment is available**; otherwise provide exact commands and mark them unverified.
6. Do not mark a lesson complete until acceptance criteria and required tests actually pass.

Use `docs/codex-lesson-guide.md` for the response template and progress-recording protocol.

Deliver lesson content directly in the discussion. Do not create files containing lesson walkthroughs. Requests to create, generate, start, or continue a lesson follow this discussion-based format.

## Architectural invariants

- **Stack:** FastAPI, SQLModel, Alembic, PostgreSQL with pgvector, Jinja2/HTMX/Alpine.js/Tailwind/daisyUI, LangGraph, Celery, Redis and pytest, as specified. Do not substitute frameworks without an approved decision.
- **Infrastructure:** Docker Compose in development and production. Dedicated **Nginx** service is the HTTP entry point; FastAPI and data services are internal. Phase 01 introduces Dockerfile, Compose, Nginx and PostgreSQL/pgvector. Redis/Celery arrive when ingestion needs them. Production TLS, SSE proxy behavior, secrets, backups and hardening are required.
- **Tenant security (Q056):** Shared PostgreSQL tables with mandatory organization-scoped access. Verify tenant ownership at every boundary, including documents, embeddings, chatbots, checkpoints and traces. Never trust a client-supplied organization ID as authorization.
- **Documents (Q057):** Canonical document/chunk embeddings per organization and embedding-model version; KB attachments reuse them. Enforce KB membership in retrieval.
- **Conversation state (Q058/Q061):** LangGraph checkpoints are authoritative for full original messages and response state. Summaries and recent-message windows are derived model context; dashboard transcripts are derived/rebuildable. Validate actual checkpointer behavior before designing persistence.
- **AI credits (Q059):** Reserve atomically before chargeable work, settle measured usage idempotently and release unused reservations. Do not invent business pricing policies.
- **Plans (Q060):** Manual provisioning during development; verified payment-provider integration required before accepting paying customers.
- **Widget:** Cross-origin iframe, domain restrictions, same-tab resumption, serialized turns and SSE completion/reconnection contracts. Nginx must not buffer streaming responses.
- **Privacy:** Retention, access control and deletion apply to transcripts, checkpoints and traces. Never log secrets or expose another tenant's data.

## Test and operational safety

- Run pytest and Alembic **inside containers** when those services exist. Commands and Compose service names must be checked against the current repository, not guessed.
- Integration tests must use **isolated test databases/queues**; never point tests or cleanup at development or production data.
- Use real PostgreSQL/pgvector, Redis and workers for integration behavior where required. Mock external provider boundaries, not the database behavior being verified.
- Do not run `docker compose down -v`, destructive migrations, mass deletes or credential rotation without explicit authorization.
- Do not commit `.env`, tokens, private keys, customer data or generated secrets.
- Keep migrations reversible when feasible; document any irreversible operation.

## Progress documentation

After a lesson is **verified**, propose an update to its row in `docs/progress-documentation/phase_1.md` (or the relevant phase tracker): status, completion date, test evidence/commit and concise notes. **Do not edit the tracker automatically unless authorized.** Do not mark implementation complete merely because code was shown, and do not mark testing complete without verified results.

Use the tracker for lesson status and the corresponding phase notes for implementation decisions, deviations, and detailed verification evidence. When authorized to update progress documentation, link to the relevant notes entry from the tracker's evidence column.

Keep lesson status, dates, decisions, and verification evidence in the tracker and phase notes. Keep navigation responsibilities and declarations in [`CODEBASE_MAP.json`](CODEBASE_MAP.json); do not put progress or test results in the index.

If the user asks for a lesson, begin with the next requested lesson (or ask which lesson only if genuinely ambiguous). If the user asks for an implementation plan, follow the existing plan rather than inventing a parallel curriculum.


## Repository navigation index

- After every authorized codebase change, assess `CODEBASE_MAP.json`: add relevant new files (including untracked additions), update changed responsibilities/declarations, rename moved paths, and remove deleted or newly excluded files. Leave unaffected entries and formatting intact; make no map change when indexed information is unchanged.
- During read-only review, report stale entries without editing. During instruction generation, include maintenance instructions in the requested artifact without applying them. Index maintenance does not authorize application or unrelated documentation edits.
- Use a flat JSON object keyed by exact, forward-slash repository-relative file paths, each mapping to a metadata object with a concise factual summary. For Python, record module namespaces, useful top-level function signatures, async/decorator metadata, class bases, and declared properties. Preserve declared types and parameter order/kinds/defaults; do not infer missing annotations. Extend consistently for other languages when introduced.
- Inspect actual source using targeted discovery and syntax-aware parsing without executing application files. Respect `.gitignore`; omit third-party dependencies, generated outputs, caches, logs, populated environment files, credentials, bodies, import lists, empty metadata, and speculative claims. Summaries suffice for configuration files. Do not recursively index documentation or lesson guides.
- Validate JSON with duplicate-key detection, normalized unique paths, file existence, metadata objects, declaration accuracy, scope exclusions, and absence of sensitive content. Do not add timestamps, implementation status, test results, or completion claims to the map.
