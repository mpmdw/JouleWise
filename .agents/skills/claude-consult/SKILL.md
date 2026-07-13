---
name: claude-consult
description: Ask Claude Fable for one bounded, read-only judgment consult from a top-level Codex session.
---

# Claude Fable consult for Codex

Use this skill only from a top-level Codex session when an independent Claude
judgment would materially improve a design choice, review, or diagnosis. It is
not an implementation path and it is never available to a Sol session that was
itself started by Claude.

## Guardrails

1. Do not use this skill if the current prompt contains
   `BRIDGE_ORIGIN: claude`. A legitimate top-level reverse call identifies its
   origin as Codex and sets its remaining hop count to zero.
2. Call the project Claude MCP `consult_fable` tool exactly once. The bridge
   itself pins model `fable`, effort `high`, plan permission mode, no session
   persistence, no slash commands, an empty MCP registry, and only Claude's
   `Read`, `Grep`, and `Glob` tools.
3. Begin the consult prompt with:

   ```text
   BRIDGE_ORIGIN: codex
   BRIDGE_HOPS_REMAINING: 0
   This is a read-only peer consult. Do not edit files, invoke Codex/Sol, start
   subagents, or delegate further.
   ```

4. Give Fable a bounded question and the minimum necessary repository context.
   Ask for findings, reasoning, risks, and a recommendation—not file changes.
5. Treat the response as advice. The top-level Codex session remains lead,
   checks the repository itself, and owns all final verification and decisions.

Never call `claude` directly, request a write-capable mode, or take another
bridge hop for this consult.
