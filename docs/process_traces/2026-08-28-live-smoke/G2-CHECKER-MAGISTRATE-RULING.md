# PR #229 (G2 checker + shakedown runsheet) — magistrate ruling (Fable, 2026-08-30)

Scope: the five NEEDS-RULING items and two honored escalations in PR #229's
gauntlet record. Authority context: D-162 (G1/G2/G3 gate), D-161 (threat-model
prune), D-164 (`_v5` supersedes `_v4` collection), D-166 (prefill length fixed
from the G2 record).

## R-1. NR-1, one-block selection: option (b), with ruled semantics

D-162 G2's own text already commits to "one block on the shakedown's own runs
root" and to the finalizer refusing "for EXACTLY the expected incompleteness
set" — a partial, one-block collection is the ruled design, so the only open
question was mechanism. RULING: option (b) — the operator terminates the
campaign run after block 1 completes, at the runsheet step that follows the
block's last member. Semantics, now ruled rather than implied: the G2
collection is DIAGNOSTIC and non-claim by construction (its runs root is not
the campaign runs root; nothing minted consumes it); the pass criterion is the
checker's refusal-set equality (`--expect-finalize-refusal`), not any
downstream artifact. Options (c) (a one-block stage frozen into the real pack)
and (d) (a runtime block selector) are REJECTED — both modify the frozen pack
or production code to serve a diagnostic; option (a) (run the full stage) is
REJECTED as defeating G2's purpose of a bounded proof. The runsheet's Phase D
gains one explicit "TERMINATE HERE" step with the exact stop command and the
expected on-disk state after termination.

## R-2. Escalated D1 (Phase D not runbook-exact): structural cure, not round 3

Two rounds failed with the same signature (hand-transcribed chain drifting
from `window_runbook.md`), so a third hand transcription is forbidden by the
standing trigger. RULING: the cure is mechanical verification — the fix round
adds a test (or extends `tests/test_check_window_provenance.py`) that EXTRACTS
the settle/screening/stage-list/bound-path steps from
`docs/phase_2/window_runbook.md` at the cited anchors (`:1516`, `:1636`,
`:1663`, `:1541`) and asserts the runsheet's Phase D chain matches, including
`$BOUND_RUNS_ROOT` vs `$RUNS_ROOT`. The runsheet is then corrected until that
test passes. If the runbook's structure defeats mechanical extraction, the
minimal alternative is a pinned side-by-side table in the runsheet whose rows
quote the runbook lines verbatim with their line anchors, checked by the same
test against the runbook bytes. Hand-transcription without a mechanical check
does not close D1.

## R-3. Escalated F1 (S11-A2 roster independence): frozen-order-manifest roster

Confirmed defect: enumerating the expected bundle set from the science
campaign manifests lets a never-written record shrink the expectation
silently. RULING (dependent on R-1): the expected roster for G2 comes from the
FROZEN order manifest / selection artifact — block 1's members as the pack
freezes them — authenticated by the pack digest, not discovered from what the
night produced. A member missing from the runs root is then a FAIL, never a
smaller expectation. The fix round implements this as the roster source for
S11-A2 with a regression in which a member's bundle is deleted and the
assertion FAILS.

## R-4. NR-3, the B4 split verdict: the applied narrow fix stands

The contract refuter is right that S11-A4 quantifies over stages actually
collected; the execution refuter is right that an empty roster passing
silently is a vacuous PASS. The applied fix (empty roster → `SKIP …
assertion_not_exercised`, never PASS) satisfies both readings and is ruled the
final disposition. No further severity adjudication owed.

## R-5. NR-4, preflight checkout path: re-cut

`preflight.sh` hard-codes `/Users/edr/JouleWise-smoke/checkout`; D-162 names
the measurement checkout. The fix round re-cuts it to
`/Users/edr/JouleWise-measurement-20260813` (or better, takes the checkout as
a required argument with that as the documented value, so the next checkout
rename is a docs change, not a script change).

## R-6. NR-2, the calibration-ledger pin advance: CONSULT, not a bench ruling

The question — whether the post-bracket advance of
`configs/calibration/calibration_ledger_head.json` during the night is an
expected reviewed change (D-161 refresh-lane shape), a freeze-span sequencing
matter (bracket → pin → freeze), or a changed-path refusal working as designed
— is entangled with the freeze-span boundaries in the runbook and the pinset
build (`build_v4_histsem_pinset.py:259-271`,
`d117_row_registry_v2.json:212-324`). The fix-round Sol session investigates
and PROPOSES with file:line evidence; the magistrate ratifies before the
shakedown night. It does NOT block merging the checker: the checker asserts
provenance, it does not consume the ledger pin.

## R-7. NR-5, `AGGREGATE_FLOOR_ARTIFACT`: unchanged

Stays NEEDS-RULING pending FLOOR-BIND-01, as the PR records.

## R-8. `_v5` re-cut note (D-164/D-166 supervening)

The runsheet's `_v4` pack references are superseded by D-164: G2 runs on the
`_v5` pack after estate 12, and D-166 binds the `_v5` prefill length to G2's
own record (512/1024/2048 resolvability). The re-cut of pack paths/digests is
MECHANICAL and deferred until the `_v5` pack is cut; it does not block this
PR. The prefill-resolvability measurement steps (three lengths on the small
model, overlap counts recorded) must be ADDED to the runsheet in the fix
round, since D-166 made G2 their source of record.

## Disposition

Fix round: one Sol high session on this branch implementing R-1, R-2, R-3,
R-5, R-8 and investigating R-6, followed by the ruled delta re-audit
(fix rounds introduce defects), then merge on green CI. The two escalations
are closed by rulings R-2 and R-3, not by further same-shape rounds.
