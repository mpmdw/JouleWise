# Draft queued row — BRACKET-EVALUATOR-PLAN-IDENTITY-01

**Status:** DRAFT for a post-`_v4` magistrate registration wave; not a live
kernel row and not implementation authority.

**Proposed priority and lane:** `p1_phase_gate`, `agent`
(`soundness-consistency`).

## Problem

The whole-window evaluator validates `--bracket-binding` against the identity
selected from the unique finalized calibration-ledger session for the exact
`runs_root`, while the finalizer validates the same binding against the
prospective manifest and plan tree (`joulewise/analysis_manifest_v3.py`, in
`_authenticate_finalization_inputs`, approximately line 3330). Refuter A
executed the divergence: a valid rechained ledger plus an alternate exact-byte
frozen plan let the producer report `BUILT` and the evaluator report `passed`,
but the finalizer refused `analysis_finalization_bracket_binding_mismatch`.
The overall chain is fail-closed, so this is a consistency gap rather than an
authorization hole: evaluator success does not yet imply finalizer identity
acceptance.

## Acceptance evidence

- The evaluator takes an independently authenticated prospective-manifest and
  plan-tree identity input and validates the bracket binding against it.
- Producer plus evaluator success implies that the finalizer accepts the same
  plan identity; no later split verdict remains possible on unchanged bytes.
- A divergence regression lands in both `tests/test_run_campaign.py` and
  `tests/test_analysis_finalizer.py`, preserving the executed alternate-plan
  counterexample and proving the cure.
- The unique-finalized-ledger-session check for the exact `runs_root` is
  unchanged; prospective identity is an additional authenticated constraint,
  not a replacement for ledger-session soundness.

## Authority and fences

- Authority: D-160 addendum (2026-08-27, #217 merged), F2.
- Fence: sequence after `_v4`; do not couple this claim/evaluation identity
  change into the frozen campaign.
- Fence: preserve the ledger-session and exact-`runs_root` checks byte-for-byte
  in meaning; this row closes only the evaluator/finalizer authority split.
- Fence: this file is a queue-row draft only. Registration belongs to a later
  kernel wave.
