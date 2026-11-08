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
