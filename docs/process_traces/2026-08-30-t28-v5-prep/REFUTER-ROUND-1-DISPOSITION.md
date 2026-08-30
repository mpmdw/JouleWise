# `_v5` prep — contract-lens refuter round 1: magistrate disposition (Fable, 2026-08-30)

Refuter: Sol xhigh, read-only, custodied at the session scratchpad out-file
(`s15-refuter-contract-out.md`; manifest row in the codex-run-v3 manifest).
Verdicts: Q1 HOLDS, Q2 FAILS (F1), Q3 HOLDS-WITH-CAVEAT (F4), Q4 HOLDS,
Q5 FAILS (F2), R-5 answered with a derivation. No refuter point rejected.

## D-1. F1 (blocker) — ACCEPTED; fix specified

The golden read-back compares the generator's registration function to itself,
so the registered falsifier can drift while its tests approve the drift —
exactly the clause the cold gate wrote (`06-COLD-GATE-RULING.md:91-95`). FIX:
the golden test pins the LITERAL frozen bytes — threshold `2.0`,
`all_must_pass: true`, comparison text, zero-denominator policy, the
comparative `kind`, and the R-5 disposition from D-3 below — as constants
written in the test file itself, compared against the emitted sub-object.
The refuter's two mutations (all_must_pass → false; threshold → 1.9) become
the regression: each must turn the suite red.

## D-2. F2 (blocker) — ACCEPTED; enforcement site RULED

Panel hashes checked only against other declarations in the same panel are a
declared-not-enforced pin (the D-157 R-2 class). The hazard is accidental
drift (a re-downloaded or updated local model) making the pre-rendered token
IDs correspond to different model bytes than the registered workload — an
evidence-identity error, so fail-closed applies (D-161 keeps fail-closed for
evidence). RULING on the site:

1. PRIMARY (production, absorbed by estate 12): at member start on the
   measurement machine, the runtime path that resolves the local model
   verifies the local `tokenizer.json` SHA-256 (and the template bytes the
   panel hash covers, if separable) against the pack-carried pin, refusing
   the member with a named reason on mismatch. The fix round implements this
   ONLY if it lands as a hash-compare at an existing model-resolution choke
   point; if it would require a new production seam, early-return
   NEEDS_RULING with the seam description (D-160 R-1 shape) instead of
   building it.
2. BELT (operational): the G2 preflight/desk script gains the same
   panel-vs-mirror hash check the custodied `admit_model_panel_entry.py`
   tool performs; that tool is refreshed against the closed panel schema in
   the fix round (its custody note already queues this).

## D-3. F3 (blocker) + R-5 — CONFIRMED AND RULED (completes cold gate R-5)

The bench check the cold gate ordered has run (Sol xhigh; derivation in the
refuter report). Confirmed: the absolute estimator is deviations-from-mean
(`detection_floor.py:917-926`), so a uniform shared shift cancels exactly and
an "absolute R_cm" under the registered comparative replay is undefined; the
comparative estimator does not recenter, so its R_cm is well-defined and
meaningful. RULED disposition, to be encoded in `dominance_criterion`:

- Absolute independent-corner R: reportable, part of the R ≥ 2 gate.
- Absolute R_cm: `not_applicable`, with the recorded reason (deviations-
  from-mean cancellation; replay registered for comparative ABBA inputs).
- Comparative R_cm: mandatory disclosure; `R_cm < 2` withdraws the dominance
  sentence (unchanged).
- No local-only absolute diagnostic is registered for `_v5` (it would need a
  distinct versioned name; deferred, not smuggled in).

This is the completion of D-165 R-5, recorded as a decision-log amendment
line with this file as authority.

## D-4. F4 (should-fix) — ACCEPTED; fix specified

The replay helper enforces the governed preconditions it claims (positive
authenticated operative bound; zero-point membership and block-delta
agreement), refusing otherwise; and the fixture test's independent arithmetic
implements the comparative floor formula itself (max / mean+t·s — a few
lines) rather than calling `comparative_false_effect_floor`, so independence
covers the entire registered arithmetic.

## Round shape

One Sol high fix round on this branch (F1, F3-encoding, F4 fully specified
above; F2 primary only at an existing choke point, else NEEDS_RULING), then
the ruled DELTA RE-AUDIT (fresh read-only Sol, distinct from the fix
session), then the execution-lens refuter question set folds into that delta
re-audit (the contract lens held on Q1/Q4, so the remaining execution risk
is concentrated in the new code the fix round writes). Merge only after the
delta re-audit returns clean and CI is green.
