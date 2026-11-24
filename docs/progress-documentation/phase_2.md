# Phase 02 — Organizations, identity and authorization: Progress Tracker

> **Source of truth:** [Implementation plan](../chathat-implementation-plan.md#phase-02--organizations-identity-and-authorization), Phase 02.\
> **Specification:** [ChatHat specification](../chathat-spec.md#3-organizations-authentication-and-authorization), section 3 (Organizations, authentication, and authorization).\
> **Progress:** 2 / 10 lessons completed (20%).\
> **Last reviewed:** 2026-11-24.

## Lesson progress

Record completed work after verification and link the relevant entry in the [Phase 02 notes](phase_2_notes.md). For a user-approved skip, link the decision and leave the completion date blank.

| Lesson | Type | Lesson name | Status | Date completed | Commit / evidence | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| P02-I01 | Implement | Organization and account data model | Completed | 2026-11-24 | [Isolated migration, ORM, and regression checks](phase_2_notes.md#p02-i01--organization-and-account-data-model) | Required organization membership and tenant-bound invitation issuer verified. |
| P02-T01 | Test | Organization and account data model | Completed | 2026-11-24 | [Focused and full pytest results](phase_2_notes.md#p02-t01--organization-and-account-data-model-tests) | Verified account and invitation persistence constraints on isolated PostgreSQL. |
| P02-I02 | Implement | Email/password authentication | Not started | — | — | — |
| P02-T02 | Test | Email/password authentication | Not started | — | — | — |
| P02-I03 | Implement | Google OAuth and account linking | Not started | — | — | — |
| P02-T03 | Test | Google OAuth and account linking | Not started | — | — | — |
| P02-I04 | Implement | Custom RBAC and tenant-scoped policies | Not started | — | — | — |
| P02-T04 | Test | Custom RBAC and tenant-scoped policies | Not started | — | — | — |
| P02-I05 | Implement | Invitation and dashboard shell | Not started | — | — | — |
| P02-T05 | Test | Invitation and dashboard shell | Not started | — | — | — |

**Status values:** `Not started`, `In progress`, `Blocked`, `Completed`, `Skipped`. Mark a lesson **Completed** when its acceptance checks pass. A completed testing lesson requires passing pytest results. A skipped lesson stays in the progress denominator.

## Completion rules

1. Follow the listed order. Each implementation lesson (`Ixx`) is immediately followed by its matching pytest lesson (`Txx`). Begin the next implementation lesson after the preceding test lesson passes.
2. Update the status when work starts, finishes, becomes blocked, or is skipped at the user's request.
3. For completed lessons, record the date and link to evidence in the phase notes. Include a commit or PR link, or the reproducible verification command and result.
4. Calculate progress as **completed rows / 10** and keep the summary above synchronized with the table.
5. Preserve prior outcomes and decisions in the phase notes when reopening a lesson.

## Phase exit checklist

- [x] PostgreSQL migrations establish organization and account tables and enforce one organization per user.
- [ ] Email/password sign-in and sign-out use secure sessions, with CSRF protection and authenticated dashboard access.
- [ ] Google OAuth validates callback state and nonce and applies the agreed account-linking policy.
- [ ] Custom roles enforce permissions and tenant boundaries on the server.
- [ ] Organization invitations and permission-gated dashboard views work, including CSRF protection for HTMX mutations.
- [ ] All 10 lesson rows are marked **Completed** with verification evidence.

## Progress notes and blockers

_Add dated entries here when a decision, failure, or deviation affects Phase 02._
