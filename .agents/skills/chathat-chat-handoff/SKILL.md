---
name: chathat-chat-handoff
description: Compress a long ChatHat discussion into one copy-ready message for a fresh chat, prioritizing the user's latest direction and preserving lesson and verification context.
---

# Prepare a ChatHat handoff

Return one concise standalone message the user can paste into a fresh chat. Start with the current objective and latest user direction. Apply recent corrections and scope changes first. Retain earlier decisions only where they still affect the next action.

- Identify ChatHat, the checkout or branch if known and relevant, the active or most recently verified lesson ID, and the precise stopping point. Identify the required paired lesson or blocking check when relevant. Use the curriculum's listed order because IDs can be out of sequence.
- Carry forward instructor mode and the latest explicit permissions or restrictions. Point the next chat to AGENTS.md, the relevant spec and plan sections, phase tracker and notes, and affected source and tests as needed. Use CODEBASE_MAP.json for targeted navigation. Include exact repo-relative paths and symbols when they help resume work.
- Distinguish code in the checkout from code only proposed in the discussion. Preserve any relevant staged or untracked work, deviations, open decisions, and run prerequisites. Distinguish observed results from user-reported results and checks still pending. Include exact test commands, results, or concise error details when needed to reproduce or interpret evidence.
- Preserve substantive constraints that could change the next decision, such as isolated PostgreSQL/pgvector testing, or a user-approved limit on lesson scope. Omit repeated explanations, stale proposals, large code dumps, raw logs, and secrets. Name any specific missing history, attachment, or state that the next chat must retrieve or recheck.
- End with the first actionable next step and any unresolved blocker. If the lesson was taught but still awaits implementation or verification, say so explicitly and preserve the correct continuation point.

Use short headings when helpful. Return the handoff alone in the current discussion. This is a summary for the user to copy. Preserve the working tree and existing chats.
