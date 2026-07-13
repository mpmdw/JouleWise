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
2. Call the project Claude MCP `consult_fable` tool exactly once. Pass the
   optional `effort` parameter: `high` (default) for ordinary consults,
   `xhigh` for judgment-dense ones; other values are rejected. The bridge
   itself pins model `fable`, plan permission mode, no session persistence,
   no slash commands, an empty MCP registry, and only Claude's `Read`,
   `Grep`, and `Glob` tools, and echoes the selection as a
   `[consult effort: ...]` first line of the result.
3. Begin the consult prompt with:

   ```text
   BRIDGE_ORIGIN: codex
   BRIDGE_HOPS_REMAINING: 0
   This is a read-only peer consult. Do not edit files, invoke Codex/Sol, start
   subagents, or delegate further.
   ```

4. Structure the request per `docs/contracts/bridge_protocol.md` §8 — provide:
   Decision question; Current Sol position; Alternatives; Evaluation criteria;
   Settled constraints; Authority order; Repository pointers (exact paths —
   Fable has read/search access, so never paste large files); Requested
   counterargument; Requested output shape.
5. Expect a `bridge-report/v1` return: the reply ends with the
   `BRIDGE_REPORT_V1` sentinel plus one JSON object on the final line. A
   missing or malformed envelope, or a transport failure, is `status: FAILED`
   — never consume it as peer approval.
6. Treat the response as advice. The top-level Codex session remains lead,
   checks the repository itself, and owns all final verification and decisions.

Never call `claude` directly, request a write-capable mode, or take another
bridge hop for this consult.
