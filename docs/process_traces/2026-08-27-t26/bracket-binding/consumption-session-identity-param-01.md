# Draft queued row — CONSUMPTION-SESSION-IDENTITY-PARAM-01

**Status:** DRAFT for a post-`_v4` magistrate registration wave; not a live
kernel row and not implementation authority.

**Proposed priority and lane:** `p2_next_slice`, `agent` (`should-fix`); the
implementation touches `joulewise/whole_window.py`.

## Problem

`AuthenticatedConsumptionSession` (approximately line 661) currently passes
the `bracket_window_id`, `bracket_plan_id`, `bracket_plan_sha256`, and
`bracket_evidence_root_id` identity arguments by calling
`bracket_binding.get(...)`. Refuter A proved this is redundant rather than
self-authorizing: mutating `plan_id` and recomputing the binding digest is still
refused against the authenticated ledger. The current shape is therefore
fail-closed, but the consumption API obscures which identity authority is
independent and makes the binding appear to supply the values against which it
is checked.

## Acceptance evidence

- `AuthenticatedConsumptionSession` receives an explicit,
  independently-authenticated bracket identity parameter; no identity field is
  extracted from the binding to authorize that same binding.
- `scripts/run_campaign.py` authenticates and threads the explicit identity for
  whole-window evaluation, and the finalizer replay threads its independently
  authenticated prospective-manifest/plan-tree identity through the same API.
- Identity extraction from `bracket_binding` is prohibited at the consumption
  call site and pinned by a source- or mutation-level regression.
- A regression preserves Refuter A's recomputed-digest mutation and proves that
  the explicit identity parameter, not a binding-owned field, determines the
  refusal.

## Authority and fences

- Authority: D-160 addendum (2026-08-27, #217 merged), F3.
- Fence: sequence after `_v4`; this is a should-fix API clarity and consistency
  row, not a pre-night blocker.
- Fence: do not weaken or remove the authenticated-ledger comparison that made
  Refuter A's mutation fail closed.
- Fence: this file is a queue-row draft only. Registration belongs to a later
  kernel wave.
