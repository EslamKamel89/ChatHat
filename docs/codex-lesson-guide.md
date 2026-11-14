# Codex Lesson Delivery Guide

This guide complements the root [`AGENTS.md`](../AGENTS.md) and the authoritative [implementation plan](chathat-implementation-plan.md). It defines **how to teach**, not new product requirements.

## Lesson delivery

Deliver every implementation and testing lesson directly in the discussion, including its explanations, code chunks, commands, and expected results. Keep lesson content in the discussion and do not create lesson-content files or a `docs/lessons/` directory. Requests to create, generate, start, or continue a lesson use this delivery format.

Repository edits for implementation and progress records follow the authorization rules in `AGENTS.md`. Record concise decisions and verified evidence in phase notes, lesson status in the tracker, and file responsibilities in the source map.

## Before every lesson

- Read the latest local specification, implementation plan, relevant progress tracker and affected source/tests.
- Report the exact lesson ID and whether its prerequisites exist. Avoid treating planned files as already implemented.
- Identify any material discrepancy between documentation and code.
- Default to **read-only teaching**. Only modify the repository if the user explicitly requests edits.

## Implementation lesson format (`Pxx-Iyy`)

1. **Purpose and mental model:** what problem this increment solves, why it belongs here and how it connects to the current architecture.
2. **Contract:** inputs, outputs, state changes, errors, dependencies and acceptance criteria.
3. **Files:** exact paths to add/change, verified against the checkout.
4. **Walkthrough:** small code sections in typing order. After each section explain the nontrivial syntax, runtime behavior, data flow and design choice. Avoid large unexplained code dumps.
5. **Run:** exact Compose-based command when available, expected observable result, and common failure causes. Never describe unexecuted commands as passed.
6. **Review:** trade-offs, security/tenant boundaries, operational implications, changed-file summary.
7. **Next lesson:** identify the immediate paired pytest lesson; do not skip it.

## Testing lesson format (`Pxx-Tyy`)

1. **Contract under test:** the exact behavior established in `Pxx-Iyy`.
2. **Test strategy:** what belongs in unit, API, database integration or end-to-end tests, and why.
3. **Fixtures:** scope, setup, isolation, cleanup and real-vs-fake boundaries.
4. **Walkthrough:** type pytest tests in coherent increments. Explain each assertion's purpose.
5. **Coverage:** success, key errors, boundaries, concurrency/idempotency and authorization where applicable. Avoid low-value combinatorial tests.
6. **Execution:** show actual commands, results and fixes if run; otherwise explicitly label results unverified.
7. **Exit:** do not advance to `Pxx-I(yy+1)` until required tests pass.

## Practical teaching rules

- Teach *why this design* before *how to type it*.
- Explain lifecycle and execution order, especially async request handling, dependency scopes, SQL transactions, worker jobs and LangGraph checkpoints.
- Use simple language for the conceptual explanation, but preserve precise technical terminology in code and contracts.
- When presenting alternatives, choose one and explain the trade-off; do not offer a menu of equivalent architectures without reason.
- Keep lessons scoped: a lesson should be runnable and independently testable.
- Explain failures as **root cause → mechanism → smallest safe fix → consequences**.
- When changes are explicitly authorized, inspect diffs and avoid unrelated edits.

## Completion record

The progress file records observed state, not intent. Use the relevant `docs/progress-documentation/phase_N.md` tracker.

| Field | Recording rule |
|---|---|
| Status | `Not started`, `In progress`, `Blocked`, or `Completed` |
| Date completed | `YYYY-MM-DD`, only after verification |
| Commit / evidence | Commit/PR or reproducible command and observed test result |
| Notes | Short decision, caveat, blocker or follow-up |

A complete implementation lesson still requires its **separate** testing lesson. Do not retroactively claim tests passed, and never auto-update the tracker without permission.

## Example lesson request

> Teach `P01-I01` using the current repository. Explain each meaningful code chunk as I type it. Do not edit files. After implementation, teach `P01-T01` separately using pytest.
