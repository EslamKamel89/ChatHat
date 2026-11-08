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
