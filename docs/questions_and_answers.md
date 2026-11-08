# ChatHat — Architecture Decision Log

## Batch 12 — Critical Architecture Decisions

**Date:** 2026-11-08
**Status:** Confirmed, with Q058 persistence-contract clarification required
**Questions:** Q056–Q060
**Specification baseline:** `docs/chathat-spec.md` v0.2.0
**Implementation status:** Not established by these decisions

### Q056 — Multi-tenant database isolation

**Selected answer:** A — Shared PostgreSQL database and shared tables, with mandatory `organization_id` filtering and application-level authorization.

**Decision:**

- Organizations share PostgreSQL tables.
- Tenant-owned records are associated with an organization.
- All tenant-sensitive reads and writes enforce organization scoping.
- Authorization is enforced server-side.
- Vector retrieval, LangGraph thread access, traces, document access, and billing operations must respect tenant boundaries.
- Separate databases or schemas per tenant are not required for the initial architecture.

**Architectural consequences:**

- SQLModel models must express tenant ownership or a securely validated tenant relationship.
- Database queries must not rely on client-provided organization identifiers as authority.
- Composite constraints and indexes should support tenant-scoped lookups.
- Tenant isolation tests must include forged identifiers, joins, vector retrieval, and checkpoint access.
- PostgreSQL row-level security may be evaluated as defense in depth; this decision does not require it.

**Affected specification requirements:**

- DATA-006: Change OPEN to CONFIRMED.
- DATA-001: Specify shared-table tenant ownership.
- AUTH-002, AUTH-004, AUTH-005: Clarify mandatory application-level tenant authorization.
- SEC-001: Enforce isolation across all persistence layers.
- RAG-002: Apply tenant and chatbot/knowledge-base retrieval filters.
- MEM-005: Validate conversation-to-tenant ownership.

**Remaining implementation details:** Index design, tenant context propagation, optional RLS, and tenant-isolation test strategy.

### Q057 — Document ingestion and embedding ownership

**Selected answer:** A — One canonical embedding/index per document and embedding-model version; knowledge bases reference shared document chunks.

**Decision:**

- Documents belong to the organization-wide library.
- A document's extracted chunks and embeddings are canonical for the applicable embedding-model version.
- Attaching a document to multiple knowledge bases does not generate duplicate embeddings.
- Knowledge bases reference documents and their canonical chunks.
- Retrieval includes only documents attached to the knowledge bases available to the chatbot.
- Re-embedding is necessary when the applicable embedding-model version changes.

**Architectural consequences:**

- Separate document ownership from knowledge-base membership.
- Represent document-to-knowledge-base relationships explicitly.
- Track embedding model/version identity.
- Enforce uniqueness/idempotency for canonical embedding records.
- Removing a document from one knowledge base must not delete shared embeddings still needed elsewhere.
- Global document deletion excludes the document from all knowledge bases and retrieval before physical cleanup.
- Ingestion publication must not expose partially completed embedding sets.

**Affected specification requirements:**

- DOC-007: Specify canonical chunk/embedding ownership.
- DOC-008: Preserve atomic publication.
- DOC-009: Preserve idempotent embedding generation.
- DOC-010: Clarify shared-reference deletion.
- DOC-013: Define embedding versioning requirements while leaving model choice open.
- DATA-004: Represent reusable documents, chunks, and cleanup.
- RAG-002: Enforce knowledge-base membership during retrieval.

**Remaining implementation details:** Chunking parameters, embedding model, reindexing migrations, and physical index strategy.

### Q058 — Consistency of conversation state

**Selected answer:** B — Treat LangGraph checkpoints as the only authority and derive all transcripts and response state from them.

**Decision:**

- Durable LangGraph checkpoints are the authoritative source for conversation state.
- Conversation transcripts and response state are derived from checkpointed information.
- The platform must not maintain an independently authoritative transcript that can contradict checkpoint state.
- Conversation state restoration must use persisted checkpoint data.
- The exact persistence and projection contract requires clarification before implementing the conversation subsystem.

**Architectural consequences:**

- Checkpointed state must preserve enough information to reconstruct the complete original transcript.
- Rolling-summary compaction must not destroy historical messages required for transcript reconstruction.
- A derived transcript projection may be maintained for dashboard queries, but it cannot be an independent authority.
- Rebuilding projections must not create duplicate messages.
- Streaming response recovery must distinguish persisted generation results from transport state.
- Historical evidence and trace retention require a defined relationship to checkpoint lifecycle.
- Checkpoint deletion, retention, and backup policies must be compatible with the 90-day transcript/trace retention requirement.
- If the selected checkpoint implementation cannot guarantee these properties, the architecture must be revisited rather than silently weakening the product requirements.

**Affected specification requirements:**

- MEM-002: Specify checkpoint authority.
- MEM-007: Reconcile separate transcript storage with checkpoint-derived transcript projections.
- MEM-008: Preserve incremental summary correctness.
- MEM-009: Preserve one active operation per conversation.
- MEM-010: Preserve synchronous summary updates.
- MEM-011: Define retention for checkpoint-authoritative history.
- DBG-002, DBG-003, DBG-009: Define reconstruction and retention of historical answer evidence.
- DATA-003: Verify the supported LangGraph checkpointer's persistence contract.
- API-003, WID-007: Recover completed streamed answers without duplicate execution.
- SEC-007: Coordinate checkpoint and derived-data deletion.

**Blocking clarification:**
Determine how the authoritative checkpoint history preserves complete original messages, durable response completion, and historical evidence independently of rolling-summary compaction.

**Status:** Decision confirmed; implementation contract unresolved.

### Q059 — Subscription usage accounting

**Selected answer:** B — Plans include monthly AI credits; each operation consumes credits based on measured model/token usage, with quota reservation before execution.

**Decision:**

- Subscription plans allocate a monthly AI credit allowance.
- AI operations consume credits according to measured model/token usage.
- Credit availability must be checked before starting chargeable work.
- A reservation is made before execution.
- Actual consumption is reconciled after execution.
- Reservations and final charges must be concurrency-safe and idempotent.

**Architectural consequences:**

- Define an internal credit ledger with reservations, charges, releases, and adjustments.
- Distinguish available, reserved, and consumed credits.
- Model-specific pricing or conversion rules must be versioned.
- Provider retries and failovers must not accidentally double-charge customers.
- Failed and interrupted operations require explicit settlement rules.
- Streaming disconnection does not automatically mean the underlying generation stopped.
- Concurrent requests must not collectively exceed available credits.

**Affected specification requirements:**

- BILL-005: Include monthly AI credit allowances.
- BILL-006: Confirm the included-credit model while leaving overage policy open.
- BILL-007: Confirm credit-based metering and measured usage.
- BILL-008: Require pre-execution reservation and post-execution reconciliation.
- DATA-005: Require an idempotent credit accounting ledger.
- NFR-010: Record AI usage and cost by organization/chatbot.

**Remaining implementation details:** Credit conversion rates, reservation estimates, refunds, renewal behavior, overages, and model-cost changes.

### Q060 — Initial release and payment dependency

**Selected answer:** A — Build and test the core product using manually provisioned plans; integrate live payments before accepting paying customers.

**Decision:**

- The core application can be developed without a live payment provider.
- Organizations may receive manually provisioned plans during development and testing.
- Subscription entitlements and usage limits must function independently of the payment provider.
- Live payment integration is required before accepting paying customers.
- The initial architecture must allow later integration without redesigning entitlement enforcement.

**Architectural consequences:**

- Separate subscription entitlements from payment-provider integration.
- Provide an authorized administrative provisioning mechanism.
- Preserve plan limits and credit accounting for manually provisioned plans.
- Introduce verified payment webhooks before the first paid production launch.
- Do not allow ordinary customers to grant themselves plans or credits.
- Record administrative changes for auditability.

**Affected specification requirements:**

- ROAD-002: Confirm payment is not required before core development or internal testing, but is required before paid launch.
- BILL-002: Payment provider remains unresolved.
- BILL-003: Preserve payment-provider abstraction.
- BILL-004: Defer live webhook integration until the paid-launch phase.
- BILL-005, BILL-008: Enforce plan entitlements and credits independently of payment provider.
- AUTH-009: Audit manual plan/credit provisioning.

**Remaining implementation details:** Payment provider, public beta eligibility, trials, billing lifecycle, refunds, and subscription renewal rules.

---

## Batch 12 — Decision Summary

| ID   | Selected | Implementation significance                          |
| ---- | -------- | ---------------------------------------------------- |
| Q056 | A        | Shared-table multi-tenancy                           |
| Q057 | A        | Canonical reusable embeddings                        |
| Q058 | B        | LangGraph checkpoints as sole conversation authority |
| Q059 | B        | Credit-based usage with reservations                 |
| Q060 | A        | Manually provisioned plans before live billing       |

## Cross-Decision Dependencies

1. Q056 requires tenant authorization for Q057 document/chunk retrieval and Q058 conversation checkpoints.
2. Q057 preserves Q012's reusable document-library model and Q016's global deletion behavior.
3. Q058 must reconcile Q036–Q044 conversation-memory and retention decisions with Q054 streaming recovery.
4. Q059 must account for Q034 model failover and Q054 server-side generation continuation.
5. Q060 allows the core product to be implemented before selecting the payment provider, but does not defer credit accounting or entitlement enforcement.

## Blocking Items

**B1 — Conversation authority and historical data:**
Q058 needs a concrete checkpoint persistence/reconstruction contract before conversation persistence is implemented.

**B2 — Credit accounting before chargeable AI execution:**
The implementation must define reservation, settlement, release, and idempotency behavior before enabling production AI usage.

**B3 — Tenant isolation:**
Shared-table organization scoping must be incorporated into the initial data model and authorization architecture.

## Important but Deferrable

- Live payment provider selection until the paid-launch integration phase.
- Exact credit pricing and plan allowances until commercial pricing is defined.
- Embedding-model selection until the ingestion/retrieval implementation phase.
- Database index optimization until representative data and load measurements exist.

**Next:** Clarify B1 before implementing the conversation persistence subsystem. No additional general-purpose questionnaire is required at this stage.

## Q061 — Authoritative Conversation History

**Date:** 2026-11-08
**Status:** CONFIRMED
**Selected answer:** A

### Decision

ChatHat shall retain the complete original conversation message history in durable LangGraph checkpoint state.

The rolling summary and recent-message window shall be constructed separately for LLM input.

Dashboard transcripts shall be derived from authoritative checkpointed history rather than maintained as an independently authoritative transcript store.

### Architectural contract

1. Every original user and assistant message must remain recoverable from authoritative checkpointed conversation history throughout its retention period.
2. Summarization must never replace, overwrite, or discard original historical messages.
3. The model receives only the applicable rolling summary, recent verbatim messages, trusted instructions, and retrieved evidence.
4. The dashboard derives the complete transcript from checkpointed history.
5. Optional transcript read projections must be rebuildable and must not become independent authorities.
6. Summary updates must preserve the correspondence between the summary and the last message summarized.
7. Conversation operations must enforce server-side serialization and idempotency.
8. Completed assistant responses must be durably recorded even when the SSE connection is interrupted.
9. Checkpoint-history retention and deletion must respect the configured conversation retention period and applicable privacy requirements.
10. Historical answer traces must preserve the evidence and configuration needed for debugging.

### Reconciliation with previous decisions

- Q058: LangGraph checkpoints remain the sole authority for conversation history and response state.
- Q036–Q037: Rolling summaries and recent-message windows remain the model-context strategy.
- Q041–Q043: Message counting, summary compression, and synchronous summarization remain unchanged.
- Q040 and Q044: Full transcripts and 90-day default retention remain required.
- Q054: Server-side generation continues after transport interruption, and completed answers remain recoverable within the same tab session.

### Specification requirements affected

MEM-002, MEM-003, MEM-004, MEM-007, MEM-008, MEM-010,
MEM-011, DBG-002, DBG-003, DBG-009, DATA-003, API-003,
WID-007, SEC-007.

### Implementation constraints

- Verify the selected LangGraph checkpointer's full-state persistence and restoration semantics.
- Measure checkpoint growth and serialization costs for long conversations.
- Design crash recovery and idempotent generation completion.
- Ensure derived transcript projections can be rebuilt.
- Define checkpoint retention and deletion without compromising historical evidence.

**Outcome:** Q058's authoritative-history ambiguity is resolved.

**Implementation status:** Not started.
