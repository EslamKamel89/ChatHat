# ChatHat — Requirements Decisions

## Batch 1 — Product Foundation

**Date:** 2026-11-08  
**Status:** Completed  
**Questions:** Q001–Q005  
**Specification:** `docs/chathat-spec.md`

### Q001 — Initial target market

**Question:** Which customers should ChatHat prioritize at launch?

**Answer:** Other — ChatHat will be a general-purpose platform serving businesses across different industries. It will provide selectable industry templates for popular business categories, including e-commerce and other industries.

**Decision implications:**

- The core chatbot architecture must remain industry-independent.
- Industry templates should provide predefined configuration defaults.
- Templates may include suggested business rules, chatbot behavior, and other relevant settings.
- Templates must be customizable after selection.
- The initial template catalog and exact template capabilities remain undecided.

**Related requirements:** PRD-007, PRD-009, BOT-002.

### Q002 — Language support

**Question:** What languages should the dashboard and chatbot support?

**Answer:** D — Fully localized dashboard and chatbot, with customer-selected languages.

**Decision implications:**

- The dashboard must support internationalization and localization.
- Customers must be able to select supported languages.
- Chatbot language configuration must be supported.
- The architecture must accommodate RTL languages.
- The initial language catalog, translation workflow, and language fallback rules remain undecided.

**Related requirements:** PRD-010, UI-001, BOT-008.

### Q003 — Organization and account structure

**Question:** How should customer accounts, organizations, and chatbots relate?

**Answer:** Other — Organizations will serve as the tenant module. A user can create an organization and automatically becomes its owner with full privileges. The owner can invite additional users and grant either owner-level permissions or restricted permissions.

**Decision implications:**

- Each organization is a tenant boundary.
- The organization creator becomes its initial owner.
- Owners have full organization-level privileges.
- Owners can add other users with owner-level or restricted permissions.
- Authorization must be enforced server-side.
- Organization resources must be tenant-isolated.
- The exact restricted permission matrix remains undecided.
- Whether users may belong to multiple organizations remains undecided.

**Related requirements:** USR-001, USR-002, USR-004, AUTH-002, AUTH-003, AUTH-004, AUTH-007.

### Q004 — Dashboard authentication

**Question:** Which sign-in methods should ChatHat support?

**Answer:** C — Email/password plus Google OAuth.

**Decision implications:**

- Support email/password authentication.
- Support Google OAuth authentication.
- Account identity must be handled consistently across both methods.
- Account linking, email verification, password recovery, and OAuth security details require further definition.

**Related requirements:** AUTH-001, AUTH-006.

### Q005 — Website visitor identity

**Question:** How should website visitors access and continue chatbot conversations?

**Answer:** B — Anonymous visitors; conversation ends when the browser tab closes.

**Decision implications:**

- Visitors do not need ChatHat accounts.
- Conversations are scoped to a browser-tab session.
- The widget must not automatically restore conversations across browser-tab sessions.
- LangGraph conversation identity must be associated with the anonymous visitor session.
- Server-side retention of conversation history, checkpoints, and debugging traces remains a separate decision.
- Session expiration and refresh behavior require further definition.

**Related requirements:** USR-003, WID-008, MEM-005, MEM-011.

---

## Batch 1 — Decision Summary

| ID   | Topic            | Decision                                                         |
| ---- | ---------------- | ---------------------------------------------------------------- |
| Q001 | Target market    | General-purpose platform with industry templates                 |
| Q002 | Localization     | Fully localized dashboard and chatbot                            |
| Q003 | Tenancy          | Organization-based tenancy with owner and restricted memberships |
| Q004 | Authentication   | Email/password and Google OAuth                                  |
| Q005 | Visitor identity | Anonymous, browser-tab-scoped conversations                      |

## Outstanding Clarifications

1. Initial industry template catalog and template customization.
2. Initial supported languages and localization fallback.
3. Restricted organization permissions and membership behavior.
4. Authentication verification, recovery, and account linking.
5. Browser refresh behavior and server-side conversation retention.

**Next batch:** Q006–Q010.

## Batch 2 — Organization Management and Industry Templates

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q006–Q010
**Specification:** `docs/chathat-spec.md`

### Q006 — Multi-organization membership

**Question:** Can the same registered user create or join more than one organization?

**Answer:** C — Each user belongs to exactly one organization.

**Decision implications:**

- Each user account belongs to exactly one organization.
- A user cannot create or join a second organization while retaining the same account.
- Organization switching is not required.
- Invitations must respect the single-organization membership constraint.
- The database must enforce this constraint, not only the UI.
- An account without an organization may exist temporarily during registration or invitation acceptance.

**Related requirements:** USR-001, USR-004, AUTH-002, DATA-001.

### Q007 — Restricted user permissions

**Question:** How should an organization owner control what invited members can access?

**Answer:** B — Custom role-based access control (RBAC): owners create roles and assign permissions.

**Decision implications:**

- Organization owners can create custom roles.
- Owners can assign permissions to roles.
- Organization members receive permissions through assigned roles.
- Authorization is enforced on the server.
- Roles and permissions must be scoped to their organization.
- Owners retain full organization-level privileges.
- The permission catalog, role-assignment rules, and protection of the last owner remain to be defined.

**Related requirements:** USR-002, AUTH-004, AUTH-007, AUTH-009.

### Q008 — Industry template behavior

**Question:** What should happen when an organization selects an industry template?

**Answer:** A — Copy predefined chatbot rules, prompts, branding, and recommended settings. Everything is editable afterward.

**Decision implications:**

- ChatHat provides predefined industry templates.
- Selecting a template copies its configuration into the chatbot.
- Copied rules, prompts, branding, and recommended settings are editable.
- The chatbot's configuration becomes independent of subsequent template updates.
- Template updates do not automatically overwrite customer customization.
- The initial template catalog and template administration remain undecided.

**Related requirements:** PRD-007, PRD-009, BOT-002, BOT-008.

### Q009 — Knowledge sharing between chatbots

**Question:** If an organization creates several chatbots, how should documents be managed?

**Answer:** D — Separate knowledge bases that can be attached to multiple chatbots.

**Decision implications:**

- Knowledge bases are independent organization-owned resources.
- A knowledge base can contain multiple documents.
- A chatbot can be connected to one or more knowledge bases.
- Multiple chatbots may use the same knowledge base.
- Document ingestion and vector storage are managed through the knowledge base.
- Retrieval must use only knowledge bases attached to the active chatbot.
- Knowledge bases cannot be attached across organization boundaries.
- Knowledge-base deletion, attachment permissions, and publication behavior require further definition.

**Related requirements:** BOT-006, DOC-001, DOC-007, RAG-002, DATA-001.

### Q010 — Chatbot configuration publishing

**Question:** When an owner changes rules, appearance, or knowledge assignments, when should visitors see the changes?

**Answer:** C — Draft and Publish workflow. Published changes apply to new conversations and subsequent messages in existing conversations.

**Decision implications:**

- Chatbots have editable draft configurations and published configurations.
- Saving a draft does not change live chatbot behavior.
- Publishing activates the new configuration.
- New conversations use the latest published configuration.
- Existing conversations use the latest published configuration on their next message.
- Configuration changes do not retroactively modify previously generated answers.
- Each answer trace should record the configuration version used.
- In-flight request behavior and publication atomicity require explicit implementation rules.

**Related requirements:** BOT-007, BOT-003, MEM-006, DBG-002, DBG-003.

---

## Batch 2 — Decision Summary

| ID   | Topic                         | Decision                                          |
| ---- | ----------------------------- | ------------------------------------------------- |
| Q006 | Multi-organization membership | Exactly one organization per user                 |
| Q007 | Authorization                 | Custom organization-scoped RBAC                   |
| Q008 | Industry templates            | Editable, independent configuration copies        |
| Q009 | Knowledge management          | Reusable knowledge bases attached to chatbots     |
| Q010 | Publishing                    | Draft/Publish; updates affect subsequent messages |

## Outstanding Clarifications

1. Organization creation, invitation acceptance, and ownership transfer.
2. Custom RBAC permission catalog and role-assignment restrictions.
3. Initial industry template catalog.
4. Knowledge-base attachment, deletion, and document publication rules.
5. Atomic chatbot publishing and behavior of in-flight requests.
6. Whether knowledge-base changes are published independently of chatbot configuration.

**Next batch:** Q011–Q015.

## Batch 3 — Knowledge Base and Document Lifecycle

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q011–Q015
**Specification:** `docs/chathat-spec.md`

### Q011 — Knowledge-base publication

**Question:** When a document is uploaded, updated, or removed from a knowledge base shared by multiple chatbots, when should the change affect chatbot answers?

**Answer:** A — Automatically after successful ingestion; every attached chatbot sees the change on its next message.

**Decision implications:**

- Knowledge bases do not require a separate Draft/Publish workflow.
- Successfully ingested documents become searchable automatically when attached to a knowledge base.
- All chatbots attached to the knowledge base can use the newly available content on their next message.
- Failed or incomplete ingestion must not expose partially processed knowledge.
- Removing a document from a knowledge base must exclude it from subsequent retrieval.
- Knowledge changes must not retroactively alter historical answers or their recorded retrieval traces.
- The system must define how concurrent ingestion, retrieval, and deletion interact.

**Related requirements:** BOT-006, BOT-007, DOC-008, DOC-010, RAG-002.

### Q012 — Document ownership and reuse

**Question:** Can a single uploaded document be used in multiple knowledge bases?

**Answer:** B — Documents belong to an organization-wide library and can be attached to multiple knowledge bases without duplicate uploads.

**Decision implications:**

- Each organization has a document library.
- Uploaded documents belong to the organization rather than to an individual chatbot or knowledge base.
- A document can be attached to multiple knowledge bases.
- A knowledge base can contain multiple documents.
- A knowledge base can be attached to multiple chatbots.
- Document storage and embedding generation should be reusable across knowledge bases.
- Retrieval must enforce both chatbot-to-knowledge-base and knowledge-base-to-document authorization.
- Removing a document from one knowledge base must not remove it from other knowledge bases.
- Deleting a document from the organization library requires a separate policy for existing attachments.

**Related requirements:** BOT-006, DOC-001, DOC-007, DATA-001, RAG-002.

### Q013 — Initial knowledge-source formats

**Question:** Which content sources should ChatHat support in its first production release?

**Answer:** C — PDF, DOCX, TXT, Markdown, CSV, XLSX, and HTML uploads.

**Decision implications:**

- The initial supported upload formats are:
  - PDF
  - DOCX
  - TXT
  - Markdown
  - CSV
  - XLSX
  - HTML
- Document ingestion must select an appropriate extraction strategy for each format.
- CSV and XLSX ingestion must preserve useful row, column, and sheet context.
- HTML ingestion must extract useful content while excluding unsafe executable elements.
- Unsupported formats must produce clear validation errors.
- Website crawling, remote URL ingestion, and external storage integrations are not included by this decision.
- Per-format limits and extraction rules remain undecided.

**Related requirements:** DOC-002, DOC-005, DOC-011, DOC-012.

### Q014 — Scanned PDFs and OCR

**Question:** How should ChatHat handle PDFs containing scanned images rather than selectable text?

**Answer:** D — Allow upload but mark pages without extractable text as skipped, with a processing report.

**Decision implications:**

- PDF ingestion does not require OCR for the initial release.
- Pages with extractable text are processed normally.
- Pages without extractable text are skipped and reported.
- The ingestion report must identify skipped pages and explain why they were skipped.
- A PDF with both readable and scanned pages can be partially ingested.
- A PDF with no usable text must not be reported as successfully searchable.
- Customers must be able to distinguish partial ingestion from complete ingestion.
- OCR remains a potential future feature.

**Related requirements:** DOC-005, DOC-006, DOC-012.

### Q015 — Document replacement and version history

**Question:** What should happen when a customer replaces an existing document?

**Answer:** D — Treat every replacement as a new document; owners manually delete the previous one.

**Decision implications:**

- Uploading a revised file creates a new document record.
- The previous document remains unchanged until explicitly deleted.
- The system does not automatically replace existing document content.
- The new document must be attached to the appropriate knowledge bases.
- Owners are responsible for removing obsolete documents.
- Historical answer traces must remain interpretable after document deletion.
- The product must not imply that a newly uploaded file automatically supersedes an older one.
- Automatic replacement, document version restoration, and rollback are not required by this decision.

**Related requirements:** DOC-010, DATA-004, DBG-003.

---

## Batch 3 — Decision Summary

| ID   | Topic                 | Decision                                              |
| ---- | --------------------- | ----------------------------------------------------- |
| Q011 | Knowledge publication | Automatic after successful ingestion                  |
| Q012 | Document ownership    | Organization library; reusable across knowledge bases |
| Q013 | Upload formats        | PDF, DOCX, TXT, MD, CSV, XLSX, HTML                   |
| Q014 | Scanned PDFs          | Skip unreadable pages and report them                 |
| Q015 | Document replacement  | New document; manual deletion of old document         |

## Outstanding Clarifications

1. Document deletion when attached to multiple knowledge bases.
2. Whether newly uploaded documents require explicit knowledge-base attachment.
3. Whether the system should warn about duplicate or outdated documents.
4. Ingestion status and reporting for partially readable files.
5. CSV/XLSX extraction, row grouping, and metadata preservation.
6. Document size, storage, page, row, and sheet limits.
7. Handling simultaneous ingestion and retrieval.
8. Whether removing a document from a knowledge base deletes any stored embeddings.

**Next batch:** Q016–Q020.

## Batch 4 — Document Library and Ingestion Rules

**Date:** 2026-11-08
**Status:** Completed — one cross-batch clarification pending
**Questions:** Q016–Q020
**Specification:** `docs/chathat-spec.md`

### Q016 — Document deletion with shared attachments

**Question:** If a document is attached to several knowledge bases, what should happen when an owner deletes it from the organization library?

**Answer:** A — Delete it from all knowledge bases after explicit confirmation, then clean up its searchable chunks.

**Decision implications:**

- Deletion is an organization-wide operation, not merely detachment from one knowledge base.
- Before deletion, the dashboard must explicitly confirm that all knowledge-base attachments will be affected.
- Deletion must make the document unavailable to all attached chatbots.
- The system must clean up its searchable chunks, embeddings, and source file according to the defined deletion lifecycle.
- Previously generated answers must not change retroactively.
- Historical retrieval traces require a separately defined retention/redaction policy.
- Deletion must be authorized and auditable.
- Cleanup failures must be retryable without restoring the document to retrieval.

**Related requirements:** DOC-010, DATA-004, RAG-002, DBG-009, AUTH-009.

### Q017 — New document attachment

**Question:** After uploading a document to the organization library, how should it become available to chatbots?

**Answer:** B — Require selecting one or more knowledge bases during upload.

**Decision implications:**

- The upload workflow requires at least one knowledge-base selection.
- Users may select multiple knowledge bases belonging to their organization.
- The uploaded document is stored once and attached to all selected knowledge bases.
- Ingestion and embedding generation must not be duplicated for each attachment.
- Knowledge-base attachment must be validated server-side.
- The document becomes searchable through its selected knowledge bases only after successful ingestion.
- Adding or removing attachments after upload requires a separate management workflow.

**Related requirements:** DOC-001, DOC-007, DOC-008, BOT-006, RAG-002.

### Q018 — Document processing and availability

**Question:** How should a document behave while ingestion is running or when only part of its content can be extracted?

**Answer:** A — Only fully successful documents become searchable; any skipped content makes ingestion fail.

**Decision implications:**

- Ingestion is all-or-nothing at the document-publication level.
- A document is not searchable while processing.
- If extraction, normalization, chunking, embedding, or persistence fails, the document must not be published.
- If any required content is skipped, ingestion must fail.
- Partial ingestion must never be reported as successful.
- Processing reports must identify skipped content and failure reasons.
- Retries must not expose partially persisted chunks.
- Failure handling must preserve tenant isolation and avoid orphaned published data.

**Cross-batch clarification:**
Q014 allows scanned PDF pages to be skipped and reported.
Q018 requires ingestion failure if any content is skipped.

The current interpretation is:

- Scanned PDFs may be uploaded.
- Unreadable pages are identified and reported.
- If any required page is skipped, the document fails ingestion and remains unsearchable.
- This interpretation must be explicitly confirmed before implementation.

**Related requirements:** DOC-005, DOC-006, DOC-008, DOC-009, DOC-012.

### Q019 — Duplicate and outdated documents

**Question:** How should ChatHat handle identical files or multiple versions of similar content?

**Answer:** C — Detect exact duplicates and block duplicate uploads within the organization.

**Decision implications:**

- ChatHat must detect exact duplicate file content within the same organization.
- An existing identical file prevents a second upload, regardless of filename.
- Duplicate detection must be enforced server-side.
- A cryptographic content hash, such as SHA-256, is the proposed mechanism.
- Concurrent uploads must not bypass duplicate prevention.
- Duplicate detection must not expose document information belonging to another organization.
- Different files containing similar or contradictory information are not automatically blocked.
- Reusing an existing document through additional knowledge-base attachments remains permitted.

**Related requirements:** DOC-001, DOC-009, DOC-014, DATA-001.

### Q020 — Initial upload limits

**Question:** How should file size and document limits be defined for the initial product?

**Answer:** B — All limits vary by subscription plan, including maximum file size.

**Decision implications:**

- Subscription plans define maximum individual file size.
- Plans may also define document count, total storage, and ingestion-related limits.
- Upload requests must be checked against current plan entitlements.
- Limits must be enforced server-side, including during concurrent uploads.
- Upload and ingestion failures must have defined quota-accounting behavior.
- Plan changes must have defined consequences for existing stored documents.
- Exact numerical limits remain undecided.

**Related requirements:** DOC-011, BILL-005, BILL-008, JOB-005.

---

## Batch 4 — Decision Summary

| ID   | Topic                 | Decision                                         |
| ---- | --------------------- | ------------------------------------------------ |
| Q016 | Document deletion     | Delete globally after explicit confirmation      |
| Q017 | Document attachment   | Select one or more knowledge bases during upload |
| Q018 | Ingestion publication | All-or-nothing; skipped content causes failure   |
| Q019 | Duplicate uploads     | Block identical files within the organization    |
| Q020 | Upload limits         | All limits vary by subscription plan             |

## Outstanding Clarifications

1. Reconcile Q014 and Q018 regarding scanned PDF pages.
2. Define whether an ingestion failure retains the original uploaded file for retry.
3. Define how duplicate uploads can attach an existing document to additional knowledge bases.
4. Define whether document deletion is immediately logical, followed by asynchronous physical cleanup.
5. Define historical trace retention after source-document deletion.
6. Define exact plan limits and quota-accounting rules.
7. Define behavior when subscription downgrades place an organization above its new limits.
8. Define whether concurrent duplicate uploads are rejected through a database uniqueness constraint or equivalent atomic mechanism.

**Next batch:** Q021–Q025.

## Batch 5 — Ingestion Failures, Deletion, and Storage Lifecycle

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q021–Q025
**Specification:** `docs/chathat-spec.md`

### Q021 — Scanned PDF conflict resolution

**Question:** Q014 allows skipped unreadable pages, but Q018 requires failure when any content is skipped. Which rule should govern?

**Answer:** B — Exception for scanned pages: skip and report unreadable PDF pages, publish readable pages; all other processing failures remain fatal.

**Decision implications:**

- Scanned or image-only PDF pages do not require OCR in the initial release.
- Pages containing extractable text are processed normally.
- Pages without extractable text are skipped and reported.
- A partially readable PDF can become searchable using its successfully extracted pages.
- Other extraction, chunking, embedding, and persistence failures remain fatal.
- A PDF containing no usable text must not be published as searchable.
- The processing report must identify skipped pages and indicate partial coverage.
- The Q021 exception supersedes the strict skipped-content rule from Q018 specifically for unreadable PDF pages.

**Related requirements:** DOC-005, DOC-006, DOC-008, DOC-012.

### Q022 — Failed ingestion and retry behavior

**Question:** If a file fails extraction or embedding, what should ChatHat retain and what can the customer do next?

**Answer:** A — Keep the original file and failed job report; allow retry without reuploading.

**Decision implications:**

- Failed ingestion does not automatically delete the uploaded source file.
- The original file remains available for retry.
- Failed jobs retain their status, error summary, and processing report.
- Authorized users can initiate another ingestion attempt.
- Retries must be idempotent and must not create duplicate searchable chunks.
- Each retry attempt should be distinguishable in job history.
- Failed content remains unavailable for retrieval until successful publication.
- Retention limits for repeatedly failing files remain undecided.

**Related requirements:** DOC-006, DOC-009, JOB-003, JOB-004.

### Q023 — Duplicate upload experience

**Question:** If the uploaded file already exists in the organization's library, what should the user experience be?

**Answer:** A — Block the duplicate and show the existing document, with an option to attach it to additional knowledge bases.

**Decision implications:**

- Exact duplicate files cannot create additional document records within the same organization.
- The user receives a clear duplicate-file response.
- The response identifies the existing document when the user is authorized to view it.
- The user can attach the existing document to additional knowledge bases.
- Reusing a document does not require uploading or embedding it again.
- Duplicate detection must remain tenant-scoped and concurrency-safe.
- An existing failed document may require retry rather than another upload; exact handling remains undecided.

**Related requirements:** DOC-001, DOC-009, DOC-014, BOT-006.

### Q024 — Document deletion and historical traces

**Question:** After an owner deletes a document, what should happen to historical answer traces that reference its content?

**Answer:** Other — Historical traces must be preserved even after the user deletes the source document. They may be needed later to debug problems with previously generated chatbot answers.

**Decision implications:**

- Deleting a source document removes it from active knowledge and retrieval.
- Historical answer traces remain available for debugging.
- Traces must preserve sufficient evidence to reconstruct which retrieved content influenced an earlier answer.
- Historical trace content must not depend on the continued existence of the source document or its vector chunks.
- Trace records should include immutable evidence snapshots and source identifiers.
- Access to historical traces must remain tenant-authorized.
- Retention duration, privacy deletion requests, and sensitive-data redaction require separate policies.
- The decision does not establish indefinite retention or override applicable legal deletion obligations.

**Related requirements:** DBG-001, DBG-003, DBG-004, DBG-009, DOC-010, MEM-011.

### Q025 — Subscription downgrade over limits

**Question:** If a customer downgrades to a plan with lower storage, document, or chatbot limits, what should ChatHat do?

**Answer:** C — Prevent the downgrade until the customer manually reduces resource usage.

**Decision implications:**

- A requested downgrade must be checked against the destination plan's limits.
- The downgrade is rejected if existing resource usage exceeds those limits.
- The dashboard must explain which limits prevent the downgrade.
- Customers must manually reduce usage before retrying.
- The system must not automatically delete documents or chatbots.
- Server-side validation must enforce downgrade eligibility.
- Billing-provider subscription changes must remain consistent with internal entitlements.
- The behavior of scheduled downgrades and externally initiated plan changes remains undecided.

**Related requirements:** BILL-005, BILL-008, BILL-009, DOC-011.

---

## Batch 5 — Decision Summary

| ID   | Topic                  | Decision                                     |
| ---- | ---------------------- | -------------------------------------------- |
| Q021 | Scanned PDFs           | Publish readable pages; report skipped pages |
| Q022 | Failed ingestion       | Retain original file and allow retry         |
| Q023 | Duplicate uploads      | Block duplicate and offer reuse              |
| Q024 | Historical traces      | Preserve evidence after source deletion      |
| Q025 | Subscription downgrade | Block downgrade until usage fits new plan    |

## Cross-Batch Reconciliation

- Q021 refines Q014 and creates a specific exception to Q018.
- Q022 extends the failure-handling behavior established by Q018.
- Q023 defines the reuse workflow required by Q012 and Q019.
- Q024 clarifies historical debugging behavior following Q016.
- Q025 defines downgrade behavior for the plan-based limits selected in Q020.

## Outstanding Clarifications

1. Trace retention duration and privacy-driven deletion.
2. Whether complete prompts and model responses are retained alongside retrieved evidence.
3. Handling duplicate files whose original ingestion failed.
4. Failed-file retention and retry limits.
5. Scheduled downgrades and payment-provider reconciliation.
6. Numerical quotas for each subscription plan.
7. How the UI distinguishes partially readable PDFs from fully processed documents.

**Next batch:** Q026–Q030.

## Batch 6 — RAG Retrieval and Answer Generation

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q026–Q030
**Specification:** `docs/chathat-spec.md`

### Q026 — Retrieval strategy

**Question:** How should ChatHat search the documents attached to a chatbot when a visitor asks a question?

**Answer:** Other — The exact retrieval steps depend on the selected industry template. For general-purpose usage, use hybrid search combining vector similarity and PostgreSQL full-text search (Option B).

**Decision implications:**

- Retrieval behavior must be configurable by industry template.
- The general-purpose template uses hybrid vector and full-text search.
- Industry-specific templates may define different retrieval strategies or processing steps.
- Retrieval must respect the chatbot's attached knowledge bases and organization boundaries.
- Template-specific retrieval must remain compatible with ChatHat's debugging and evidence-tracing system.
- The exact retrieval pipelines for individual industries remain undecided.
- Whether customers can modify retrieval settings after selecting a template remains undecided.

**Related requirements:** PRD-009, BOT-002, RAG-001, RAG-002, RAG-003.

### Q027 — Insufficient knowledge behavior

**Question:** What should the chatbot do when its knowledge bases do not contain enough information to answer a visitor's question?

**Answer:** C — State that the information is unavailable and offer a configurable contact or support action.

**Decision implications:**

- The chatbot must not invent unsupported information when evidence is insufficient.
- It must clearly communicate that the requested information is unavailable.
- The organization can configure a contact or support action.
- The fallback behavior must work across supported languages.
- The system must define how insufficient evidence is detected.
- The available support-action types and their configuration remain undecided.

**Related requirements:** RAG-006, BOT-008, WID-010.

### Q028 — AI model configuration

**Question:** How much control should organization owners have over the language model used by their chatbots?

**Answer:** A — ChatHat selects and manages the model centrally; customers cannot change it.

**Decision implications:**

- ChatHat controls model selection, provider credentials, and model configuration.
- Customers cannot directly select language models.
- Customers do not need to supply model API keys.
- The platform must be able to update or replace models centrally.
- Model usage must remain measurable for billing and operational monitoring.
- Debugging traces should record which model and configuration generated each answer.
- The initial model provider and model-selection policy remain undecided.

**Related requirements:** RAG-007, AI-001, BILL-005, DBG-003.

### Q029 — Conversation-aware retrieval

**Question:** When visitors ask follow-up questions, how should ChatHat determine what to retrieve?

**Answer:** D — Use the latest message first; perform contextual rewriting only when the system detects ambiguity.

**Decision implications:**

- The visitor's latest message is the initial retrieval-query candidate.
- The system must determine whether the message depends on earlier conversation context.
- When context is needed, the system rewrites the message into a standalone retrieval query.
- Unambiguous questions should avoid unnecessary rewriting.
- Retrieval-query rewriting must not silently introduce unsupported facts.
- Debugging traces should record the original query, ambiguity decision, and rewritten query when applicable.
- The ambiguity-detection mechanism remains undecided.

**Related requirements:** RAG-003, MEM-001, MEM-004, DBG-003.

### Q030 — Sources displayed to visitors

**Question:** Should chatbot answers show which knowledge documents were used?

**Answer:** A — No visitor-facing citations; only organization owners can inspect evidence in the dashboard.

**Decision implications:**

- Visitor-facing chatbot answers do not display source citations.
- The platform must still capture retrieval evidence internally.
- Organization owners can inspect evidence through the debugging dashboard.
- Source metadata and retrieved content must be preserved sufficiently for historical debugging.
- Evidence access must be protected by organization-level authorization.
- Visitor-facing citation configuration is not required.
- The relationship between owner-only access and custom RBAC permissions requires clarification.

**Related requirements:** WID-010, DBG-001, DBG-002, DBG-003, AUTH-007.

---

## Batch 6 — Decision Summary

| ID   | Topic                 | Decision                                                    |
| ---- | --------------------- | ----------------------------------------------------------- |
| Q026 | Retrieval             | Industry-template-specific; hybrid search for general usage |
| Q027 | Insufficient evidence | Explain limitation and offer configurable support action    |
| Q028 | Model selection       | Centrally managed by ChatHat                                |
| Q029 | Follow-up questions   | Rewrite only when contextual ambiguity is detected          |
| Q030 | Visitor citations     | None; evidence visible to organization owners               |

## Cross-Batch Reconciliation

- Q026 extends Q008: industry templates can define retrieval behavior in addition to rules, prompts, branding, and recommended settings.
- Q026 preserves Q009 and Q012: retrieval must respect reusable knowledge-base and document relationships.
- Q028 establishes centrally managed model selection without customer-supplied API keys.
- Q029 must work with the LangGraph conversation-memory architecture.
- Q030 reinforces Q024: historical evidence must remain inspectable even after a source document is deleted.

## Outstanding Clarifications

1. Retrieval strategies for individual industry templates.
2. Whether template retrieval settings are editable after selection.
3. Hybrid-search ranking and fusion strategy.
4. Insufficient-evidence detection and support-action configuration.
5. Initial AI provider, model, and failover policy.
6. Ambiguity detection and contextual-query rewriting.
7. Evidence-dashboard access for restricted organization roles.
8. Retrieval quality evaluation and observability.

**Next batch:** Q031–Q035.

## Batch 7 — Retrieval Quality and AI Reliability

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q031–Q035
**Specification:** `docs/chathat-spec.md`

### Q031 — Industry-specific retrieval customization

**Question:** After selecting an industry template, how much control should an organization have over its retrieval strategy?

**Answer:** A — Retrieval is fully managed by ChatHat; customers cannot modify it.

**Decision implications:**

- ChatHat controls retrieval algorithms, parameters, and execution pipelines.
- Industry templates determine the appropriate retrieval strategy.
- Customers cannot directly edit retrieval internals.
- ChatHat may improve retrieval behavior centrally without requiring customer configuration.
- Customer-editable chatbot rules and branding remain separate from retrieval internals.
- Internal retrieval configurations should be versioned for reproducible debugging.
- Template-specific retrieval pipelines remain to be defined.

**Related requirements:** PRD-009, BOT-002, RAG-001, RAG-003.

### Q032 — Hybrid retrieval ranking

**Question:** For the general-purpose hybrid pipeline, how should vector and full-text search results be combined?

**Answer:** A — Use Reciprocal Rank Fusion (RRF) to combine ranked results.

**Decision implications:**

- The general-purpose retrieval pipeline combines vector similarity search with PostgreSQL full-text search.
- Reciprocal Rank Fusion combines the ranked results.
- RRF uses rank positions rather than directly combining incompatible raw scores.
- Results referring to the same chunk must be deduplicated before final selection.
- The fusion constant, retrieval depth, and final context size remain platform-managed configuration.
- Debugging traces should preserve each search branch's ranks and the fused ranking.
- Tenant and knowledge-base filtering must apply to both search branches.

**Related requirements:** RAG-001, RAG-002, RAG-003, DBG-003.

### Q033 — Insufficient-evidence detection

**Question:** How should ChatHat decide whether the retrieved knowledge supports an answer?

**Answer:** B — Use retrieval scores plus an LLM assessment of whether the evidence supports the answer.

**Decision implications:**

- Evidence sufficiency is evaluated using retrieval signals and an LLM-based assessment.
- Retrieval scores alone do not determine whether an answer is supported.
- The LLM assessment must consider the visitor's question and retrieved evidence.
- Unsupported questions trigger the configured insufficient-knowledge response and support action.
- Assessment decisions and relevant inputs must be captured for debugging.
- The assessment model, thresholds, and handling of contradictory evidence remain undecided.
- The assessment must not be treated as an infallible guarantee against hallucinations.

**Related requirements:** RAG-006, RAG-007, DBG-003.

### Q034 — AI provider failure handling

**Question:** What should happen when ChatHat's primary AI model provider is unavailable or repeatedly fails?

**Answer:** D — Use bounded retries followed by a compatible backup provider, with all attempts recorded for debugging.

**Decision implications:**

- ChatHat uses a primary AI provider and a compatible fallback provider or model.
- Transient failures trigger bounded retries.
- Retries must use controlled backoff and respect request deadlines.
- After retry exhaustion, ChatHat attempts the configured fallback.
- Each attempt must be recorded with provider, model, outcome, and relevant timing/error metadata.
- If all providers fail, the visitor receives a clear temporary-error response.
- Retrying must not create duplicate conversation messages or other side effects.
- Provider selection, timeout budgets, retry counts, and fallback compatibility remain undecided.

**Related requirements:** RAG-007, AI-001, DBG-003, OPS-005.

### Q035 — Support action on unanswered questions

**Question:** When a chatbot cannot answer from its knowledge, what type of customer-configurable support action should it offer?

**Answer:** D — Multiple action types, including links and an optional built-in contact form, configurable per chatbot.

**Decision implications:**

- Each chatbot can configure support actions for unanswered questions.
- Support actions may include external contact links.
- Chatbots may offer an optional built-in contact form.
- Contact-form submissions must be associated with the correct organization and chatbot.
- Submitted information must be protected by tenant authorization and privacy controls.
- Form delivery, notification destinations, validation, and retention require further decisions.
- The widget must present support actions in its configured language.

**Related requirements:** BOT-008, WID-010, RAG-006, DATA-001.

---

## Batch 7 — Decision Summary

| ID   | Topic                       | Decision                                       |
| ---- | --------------------------- | ---------------------------------------------- |
| Q031 | Retrieval customization     | Platform-managed, not customer-editable        |
| Q032 | Hybrid ranking              | Reciprocal Rank Fusion                         |
| Q033 | Evidence sufficiency        | Retrieval signals plus LLM assessment          |
| Q034 | AI reliability              | Bounded retries, fallback, and attempt tracing |
| Q035 | Unanswered-question support | Configurable links and optional contact form   |

## Cross-Batch Reconciliation

- Q031 clarifies Q026: industry templates select retrieval behavior, but customers cannot modify retrieval internals.
- Q032 specifies the ranking method for Q026's general-purpose hybrid search.
- Q033 defines the evidence-sufficiency approach for Q027.
- Q034 extends Q028: ChatHat centrally manages primary and backup AI providers.
- Q035 defines the configurable support actions required by Q027.
- Q034 and Q033 extend Q024's historical debugging requirement to include provider attempts and evidence assessments.

## Outstanding Clarifications

1. RRF fusion constant, candidate counts, and context limits.
2. Evidence-sufficiency assessment schema and decision thresholds.
3. Contradictory or partially relevant evidence handling.
4. Primary and backup model/provider selection.
5. Retry limits, deadlines, and failover triggers.
6. Support-action types and built-in form fields.
7. Contact-form notification, storage, and privacy rules.
8. Whether provider failures consume customer usage quotas.

**Next batch:** Q036–Q040.

## Batch 8 — Conversation Memory and LangGraph State

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q036–Q040
**Specification:** `docs/chathat-spec.md`

### Q036 — Conversation memory structure

**Question:** How should ChatHat represent conversation history when the conversation becomes too long to fit efficiently into the model context?

**Answer:** B — Keep recent messages verbatim and maintain a rolling summary of older conversation history.

**Decision implications:**

- Conversation memory consists of a rolling summary and a recent-message window.
- Recent messages are provided to the model in their original form.
- Older messages are represented by a continuously updated summary.
- The complete conversation transcript must remain separately available for dashboard inspection.
- Summarization must not modify the original stored messages.
- The rolling summary is used for context management, not as a replacement for historical records.

**Related requirements:** MEM-001, MEM-002, MEM-003, MEM-004.

### Q037 — When to update the rolling summary

**Question:** If ChatHat uses a rolling summary, when should it summarize older conversation messages?

**Answer:** Other — Maintain a configurable number of verbatim messages. Whenever the conversation grows beyond that window, merge the oldest messages outside the window into the existing rolling summary.

**User-provided example:**

With a verbatim window of 3 messages:

- At 5 messages:
  - Summary covers messages 1–2.
  - Messages 3–5 remain verbatim.
- When message 6 is added:
  - Update the summary using the previous summary plus message 3.
  - Messages 4–6 remain verbatim.

**Decision implications:**

- The verbatim window size is configurable.
- The window is measured in messages, not necessarily conversation turns.
- Summarization is incremental rather than rebuilding the summary from the entire transcript.
- Once a message moves into the summary, it is removed from the verbatim model-context window.
- A new message can cause the oldest verbatim message to be merged into the summary.
- Each message must be summarized exactly once as the window advances.
- The summary update must preserve relevant facts and conversational context.
- The original messages remain stored independently of the summary.
- The exact counting rules for system, tool, user, and assistant messages remain undecided.
- Token-budget safeguards may still be required for unusually long individual messages.

**Related requirements:** MEM-002, MEM-003, MEM-004, MEM-007.

### Q038 — Visitor session and page refresh

**Question:** Batch 1 established that conversations end when the browser tab closes. What should happen if a visitor refreshes the same tab?

**Answer:** A — Preserve the conversation on refresh, but do not intentionally restore it after the tab closes.

**Decision implications:**

- Refreshing the same browser tab preserves the visitor's conversation.
- The widget restores the active conversation after a normal refresh.
- Closing the tab ends the visitor's ability to resume that conversation.
- Browser-tab-scoped storage may be used for session identity.
- Server-side conversation and debugging records may outlive the browser-tab session.
- Session identifiers must be validated and scoped to the correct chatbot.
- Browser session restoration and duplicated-tab behavior require implementation rules.

**Related requirements:** USR-003, WID-008, MEM-005.

### Q039 — Concurrent messages in one conversation

**Question:** What should happen if a visitor sends another message while the previous answer is still generating?

**Answer:** A — Disable sending another message until the current response completes.

**Decision implications:**

- Only one answer-generation operation is permitted per conversation at a time.
- The widget disables additional message submission while a response is generating.
- Server-side concurrency protection is required because frontend disabling alone is insufficient.
- Conversation memory and LangGraph state updates must remain sequential.
- Duplicate requests must not produce duplicate messages or corrupt conversation state.
- Failure, timeout, or cancellation must release the conversation for another message.
- The exact cancellation and stale-lock recovery policies remain undecided.

**Related requirements:** MEM-006, MEM-008, WID-009, OPS-005.

### Q040 — Conversation history visibility

**Question:** Which conversation information should organization owners be able to inspect in the dashboard?

**Answer:** D — Full transcript and debugging traces, with configurable retention and access controls.

**Decision implications:**

- Authorized organization users can inspect full conversation transcripts.
- Associated debugging traces are accessible from conversation history.
- Transcript and trace retention are configurable.
- Access is controlled through organization-scoped authorization.
- Historical traces remain available after source-document deletion, subject to the configured retention and applicable privacy requirements.
- The system must distinguish raw transcripts from rolling memory summaries.
- Retention defaults, maximum durations, and restricted-role permissions remain undecided.

**Related requirements:** MEM-011, DBG-001, DBG-002, DBG-009, AUTH-007.

---

## Batch 8 — Decision Summary

| ID   | Topic               | Decision                                                                 |
| ---- | ------------------- | ------------------------------------------------------------------------ |
| Q036 | Memory structure    | Rolling summary plus verbatim recent messages                            |
| Q037 | Summary updates     | Incremental updates when messages leave the configurable verbatim window |
| Q038 | Refresh behavior    | Preserve conversation on refresh; end on tab close                       |
| Q039 | Concurrent messages | One active response per conversation                                     |
| Q040 | Dashboard history   | Full transcript and traces with configurable retention and access        |

## Cross-Batch Reconciliation

- Q037 specifies the rolling-summary algorithm selected in Q036.
- Q038 clarifies the browser-tab session behavior selected in Q005.
- Q039 protects the sequential memory updates required by Q037.
- Q040 supports Q024's requirement to preserve historical debugging evidence after source-document deletion.
- Q040 must operate within the organization-scoped RBAC model selected in Q007.

## Outstanding Clarifications

1. Whether the verbatim window counts individual messages or complete user/assistant exchanges.
2. Whether system and tool messages count toward the window.
3. Maximum summary length and behavior when a summary becomes too large.
4. Whether summarization runs synchronously or asynchronously.
5. Handling failed summary updates and concurrent conversation requests.
6. Browser-tab duplication and browser session restoration.
7. Default transcript/trace retention and privacy controls.
8. Restricted-role permissions for transcript and trace inspection.

**Next batch:** Q041–Q045.

## Batch 9 — Memory Lifecycle and Conversation Retention

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q041–Q045
**Specification:** `docs/chathat-spec.md`

### Q041 — Verbatim window counting

**Question:** What exactly should count toward the configurable recent-message window?

**Answer:** A — Individual user and assistant messages; system and tool messages are excluded.

**Decision implications:**

- The verbatim window counts individual user and assistant messages, not complete exchanges.
- System and tool messages do not count toward the configured window size.
- A window size of three means three individual user/assistant messages.
- Older user/assistant messages are incrementally merged into the rolling summary.
- System instructions remain separately managed and are not removed because the verbatim window advances.
- Tool-message storage and model-context inclusion require separate rules.
- The complete original conversation transcript remains stored independently of the rolling summary.

**Related requirements:** MEM-001, MEM-002, MEM-003, MEM-004.

### Q042 — Rolling summary size control

**Question:** What should ChatHat do when the accumulated rolling summary becomes too long?

**Answer:** B — Apply a maximum token budget and periodically compress the existing summary while preserving important context.

**Decision implications:**

- Rolling summaries have a configurable maximum token budget.
- Summary updates must respect that budget.
- When necessary, the existing summary is compressed while preserving important conversational context.
- Compression must not change the original stored transcript.
- The system must track the last message included in the summary.
- Summary compression and incremental updates must be retry-safe.
- The exact token limit, compression strategy, and preservation criteria remain undecided.

**Related requirements:** MEM-003, MEM-004, MEM-007.

### Q043 — Summary update execution

**Question:** When a message leaves the verbatim window, how should its summary update be executed?

**Answer:** A — Synchronously within the conversation request before generating the next answer.

**Decision implications:**

- Required summary updates occur during the active conversation request.
- The summary must be updated before the next answer is generated.
- Answer generation uses the updated summary and current verbatim window.
- The summary update and its cursor must be persisted consistently.
- A failed summary update must not silently advance the summary cursor.
- Only one state-changing conversation operation may execute at a time.
- Summarization latency becomes part of the response-time budget.
- Failure recovery and retry behavior remain to be defined.

**Related requirements:** MEM-003, MEM-006, MEM-007, MEM-008.

### Q044 — Transcript and trace retention

**Question:** What should be the default policy for stored visitor conversations and debugging traces?

**Answer:** B — Retain for 90 days by default, with organization-configurable retention within platform limits.

**Decision implications:**

- The default retention period for transcripts and debugging traces is 90 days.
- Organizations can configure retention within platform-defined limits.
- Expired records must be removed through an automated retention process.
- Historical traces remain available after source-document deletion only while they remain within their applicable retention period.
- Retention applies independently of browser-tab session lifetime.
- Privacy-related deletion requests may require earlier removal.
- The permitted retention range, deletion schedule, and backup-handling rules remain undecided.

**Related requirements:** MEM-011, DBG-009, DATA-004, OPS-005.

### Q045 — Dashboard access to sensitive conversation data

**Question:** How should custom organization roles control access to visitor transcripts and debugging evidence?

**Answer:** C — Any organization member with chatbot management permission can inspect all transcripts and traces.

**Decision implications:**

- Organization owners have full access to their organization's transcripts and debugging traces.
- Other organization members gain transcript and trace access through chatbot management permission.
- A separate transcript-viewing permission is not required by this decision.
- A separate debugging-trace permission is not required by this decision.
- All transcript and trace queries must enforce organization-level authorization.
- Users without chatbot management permission cannot inspect these records.
- The meaning of "all transcripts and traces" across multiple chatbots requires explicit confirmation.
- The dashboard should make the data-access consequences of granting chatbot management permission clear.

**Related requirements:** AUTH-007, AUTH-009, DBG-001, DBG-002, MEM-011.

---

## Batch 9 — Decision Summary

| ID   | Topic                 | Decision                                                         |
| ---- | --------------------- | ---------------------------------------------------------------- |
| Q041 | Verbatim window       | Individual user/assistant messages                               |
| Q042 | Summary size          | Token budget with periodic compression                           |
| Q043 | Summary execution     | Synchronous before answer generation                             |
| Q044 | Data retention        | 90 days by default; configurable within limits                   |
| Q045 | Sensitive-data access | Chatbot management permission grants transcript and trace access |

## Cross-Batch Reconciliation

- Q041 defines the message-counting rule for Q037.
- Q042 adds bounded summary growth to Q036 and Q037.
- Q043 establishes the execution timing for the rolling-summary algorithm.
- Q044 defines the default retention policy for Q024 and Q040.
- Q045 clarifies access to historical evidence under the custom RBAC model selected in Q007.
- Q045 also clarifies Q030: organization owners and authorized chatbot managers can inspect internal evidence, while website visitors cannot see citations.

## Outstanding Clarifications

1. Maximum and minimum configurable retention periods.
2. Exact rolling-summary token budget and compression behavior.
3. Summary-update failure recovery.
4. Whether chatbot management permission grants access across every chatbot or only managed chatbots.
5. Handling of system and tool messages in model context.
6. Retention cleanup scheduling and backup deletion.
7. Privacy-driven deletion of transcripts and debugging evidence.
8. How retention configuration changes affect existing records.

**Next batch:** Q046–Q050.

## Batch 10 — Chatbot Widget and Website Integration

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q046–Q050
**Specification:** `docs/chathat-spec.md`

### Q046 — Website domain authorization

**Question:** Which websites should be allowed to load and use an organization's embedded chatbot?

**Answer:** C — Registered domains in production, with a separate testing mode for localhost and staging.

**Decision implications:**

- Production chatbot usage is restricted to registered domains.
- Each chatbot must have a domain authorization configuration.
- Localhost and staging environments are supported through a separate testing mode.
- Production domain restrictions must not be bypassed through testing configuration.
- Domain validation must be enforced server-side for widget requests.
- The widget's public identifier is not a secret and must not serve as its sole authorization mechanism.
- Allowed-origin matching rules, staging-domain registration, and testing-mode access controls remain undecided.

**Related requirements:** WID-001, WID-003, WID-004, SEC-005.

### Q047 — Widget customization

**Question:** How much control should customers have over their chatbot's appearance?

**Answer:** B — Advanced customization: basic settings plus fonts, dimensions, launcher icon, and message styles.

**Decision implications:**

- Customers can customize chatbot name, logo, primary color, welcome message, and position.
- Customers can also configure fonts, dimensions, launcher icon, and message styling.
- Widget appearance settings belong to chatbot configuration.
- Appearance changes follow the chatbot Draft/Publish workflow selected in Q010.
- Published appearance changes affect the widget after the new configuration is loaded.
- Custom CSS injection is not required.
- Allowed fonts, dimensions, colors, and responsive constraints remain undecided.

**Related requirements:** BOT-003, BOT-007, WID-005, WID-006.

### Q048 — Widget installation method

**Question:** How should customers install ChatHat on their websites?

**Answer:** B — JavaScript snippet plus an optional custom HTML container for inline embedding.

**Decision implications:**

- ChatHat provides a JavaScript installation snippet.
- The default integration creates a floating chatbot widget.
- Customers may alternatively mount the chatbot inside a designated HTML container.
- Both integration modes must use the same chatbot identity, configuration, security rules, and conversation API.
- The widget must avoid interfering with the host website's styles and scripts.
- Framework-specific SDKs are not required for the initial release.
- Script-loading behavior, inline container configuration, and compatibility requirements remain undecided.

**Related requirements:** WID-001, WID-002, WID-005.

### Q049 — Chatbot availability controls

**Question:** How should owners control whether their published chatbot accepts visitor messages?

**Answer:** C — Manual enable/disable plus business-hours scheduling and an offline support action.

**Decision implications:**

- Organization owners can manually enable or disable a chatbot.
- Each chatbot can have a business-hours schedule.
- The chatbot becomes unavailable outside configured operating hours.
- When unavailable, the widget presents a configurable offline message and support action.
- Availability must be enforced server-side, not only in the widget UI.
- Schedule evaluation must use a defined time zone.
- Manual override precedence, holidays, overnight schedules, and in-progress conversation behavior remain undecided.

**Related requirements:** BOT-007, BOT-008, WID-009, WID-010.

### Q050 — Widget response delivery

**Question:** How should AI-generated answers appear to website visitors?

**Answer:** B — Stream generated text progressively using Server-Sent Events (SSE).

**Decision implications:**

- ChatHat streams AI-generated response text progressively to the widget.
- The widget renders partial answer content as it arrives.
- SSE is the selected server-to-client streaming mechanism.
- A completed response must be persisted as the authoritative assistant message.
- Streaming interruptions must not corrupt conversation state.
- The widget must distinguish partial, completed, failed, and cancelled responses.
- Streaming endpoints must enforce chatbot, session, and domain authorization.
- Reconnection, timeout, cancellation, and usage-accounting behavior remain undecided.

**Related requirements:** WID-007, WID-009, MEM-006, OPS-005.

---

## Batch 10 — Decision Summary

| ID   | Topic                | Decision                                             |
| ---- | -------------------- | ---------------------------------------------------- |
| Q046 | Domain authorization | Registered production domains; separate testing mode |
| Q047 | Appearance           | Advanced widget customization                        |
| Q048 | Installation         | JavaScript snippet and optional inline container     |
| Q049 | Availability         | Manual controls, business hours, offline support     |
| Q050 | Response delivery    | Server-Sent Events streaming                         |

## Cross-Batch Reconciliation

- Q046 adds deployment restrictions to the widget integration model.
- Q047 follows Q010: appearance settings must use Draft/Publish.
- Q048 supports both floating and inline embedding without separate chatbot implementations.
- Q049 extends Q027 and Q035: offline support actions are available when the chatbot cannot accept messages.
- Q050 must respect Q039: one active response per conversation.
- Q050 must also respect Q038: refreshing a tab can restore the conversation, but not necessarily an interrupted stream.

## Outstanding Clarifications

1. Domain matching rules, subdomains, and local testing authorization.
2. Widget isolation from host-page CSS and JavaScript.
3. Allowed customization values and responsive behavior.
4. Business-hours time zones, holidays, and manual override precedence.
5. Whether an already-started response continues when business hours end.
6. SSE stream lifecycle, reconnection, cancellation, and timeout behavior.
7. How interrupted streams are persisted and billed.
8. Whether widget configuration is cached and how published updates invalidate it.

**Next batch:** Q051–Q055.

## Batch 11 — Widget Security, Availability, and Streaming Lifecycle

**Date:** 2026-11-08
**Status:** Completed
**Questions:** Q051–Q055
**Specification:** `docs/chathat-spec.md`

### Q051 — Production domain matching

**Question:** How should registered production domains be matched against websites embedding a chatbot?

**Answer:** B — Allow exact hostnames and explicitly configured wildcard subdomains.

**Decision implications:**

- Production domain authorization supports exact hostnames.
- Explicit wildcard rules may authorize subdomains.
- Registering a root domain does not automatically authorize every subdomain.
- Domain patterns must be validated and normalized.
- The backend must enforce configured domain rules.
- Wildcard matching must respect hostname boundaries.
- Rules for ports, schemes, public suffixes, and internationalized domains remain to be specified.

### Q052 — Widget isolation from host websites

**Question:** How should the embedded widget avoid CSS conflicts and JavaScript interference from the customer's website?

**Answer:** B — Render the widget inside a cross-origin iframe, controlled by a lightweight JavaScript loader.

**Decision implications:**

- The installation snippet loads a lightweight JavaScript bootstrap.
- The chatbot interface runs inside a cross-origin iframe.
- Floating and inline installations share the same isolation architecture.
- Host-page styles must not directly affect iframe contents.
- Host-page communication must use a validated cross-origin messaging contract.
- Iframe permissions, sandbox settings, and Content Security Policy compatibility remain to be specified.

### Q053 — Business-hours and manual override

**Question:** What should happen when a chatbot's manual availability setting conflicts with its business-hours schedule?

**Answer:** B — Manual enable and disable both override the schedule until the owner removes the override.

**Decision implications:**

- Availability supports three logical manual states: automatic, forced online, and forced offline.
- Automatic mode follows the configured business-hours schedule.
- Forced online bypasses the schedule until explicitly removed.
- Forced offline bypasses the schedule until explicitly removed.
- The backend must enforce effective availability.
- Time zones, holiday calendars, and active-stream behavior remain to be specified.

### Q054 — Streaming interruption behavior

**Question:** If a visitor loses connection while an answer is streaming, how should ChatHat handle the generation?

**Answer:** A — Continue generation on the server, save the completed answer, and show it if the visitor reconnects within the same tab session.

**Decision implications:**

- Browser disconnection does not automatically cancel generation.
- Generation continues server-side after a stream interruption.
- The completed answer is persisted once.
- Reconnection within the same tab session retrieves the completed answer.
- Reconnection must not start duplicate generation.
- The system must distinguish generation state from transport connection state.
- Generation deadlines, reconnection authentication, and cleanup policies remain undecided.

### Q055 — Widget abuse protection

**Question:** Which protection strategy should ChatHat use to prevent excessive or automated chatbot usage?

**Answer:** B — Apply layered limits by IP address, visitor session, chatbot, and organization, with optional challenge mechanisms.

**Decision implications:**

- Enforce layered rate limits across IP address, visitor session, chatbot, and organization.
- Rate limits complement subscription quotas rather than replace them.
- Optional challenge mechanisms may be triggered for suspicious usage.
- Limit checks must be enforced server-side.
- Distributed deployments require consistent shared rate-limit state.
- Exact thresholds, challenge provider, and response behavior remain undecided.

---

## Batch 11 — Decision Summary

| ID   | Topic               | Decision                                                     |
| ---- | ------------------- | ------------------------------------------------------------ |
| Q051 | Domain matching     | Exact hostnames and explicit wildcard subdomains             |
| Q052 | Widget isolation    | Cross-origin iframe and lightweight JavaScript loader        |
| Q053 | Manual override     | Forced online/offline overrides schedule until removed       |
| Q054 | Stream interruption | Continue generation, persist answer, restore within same tab |
| Q055 | Abuse protection    | Layered rate limits with optional challenges                 |

## Cross-Batch Reconciliation

- Q051 specifies the production-domain rules introduced by Q046.
- Q052 establishes the isolation mechanism for the floating and inline installations selected in Q048.
- Q053 resolves the manual-override precedence left open by Q049.
- Q054 defines disconnection behavior for the SSE streaming selected in Q050.
- Q054 must preserve the single-active-response invariant established by Q039.
- Q055 strengthens the public-widget protection required by Q046.

## Outstanding Clarifications

1. Exact wildcard-domain validation and origin matching.
2. Iframe permissions, CSP requirements, and postMessage contracts.
3. Availability schedules, time zones, holidays, and overnight periods.
4. Stream execution deadlines and server-side continuation mechanism.
5. Reconnection identity and response-recovery endpoint.
6. Rate-limit thresholds, challenge triggers, and distributed state.
7. Billing treatment of completed responses that were never viewed.
