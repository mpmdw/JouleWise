# Night-hardening findings register (2026-08-07; Sol high/fast lenses 1-2 of 3)

Charge: defects that would strand one of the three D-117 quiet nights.
Full reports in this directory (lens 3, extraction/mint, pending).
Magistrate triage below; dispositions assigned at the pre-window
readiness gate (memo gate 2/8).

## Lens 1 — campaign runner/admission (AUDIT-RUNNER.md)

- R6 MAJOR: relative `--runs-dir` PATH-DOUBLING is STILL LIVE in the
  whole-window verdict (run_campaign.py:5148 / whole_window.py:1876) —
  a relative root collects fine then fails verdict issuance.
  MITIGATION NOW: D-117 plans + operator packet freeze ABSOLUTE runs
  roots. FIX candidate for the night-hardening unit.
- R7 SHOULD-FIX: verdict is unbounded/serial/opaque and empirically
  >2 min — operator kill leaves a stale campaign.lock. MITIGATION:
  operator packet forbids killing verdict; add progress/deadline later.
- R5: cooldown/cap arithmetic uses wall clock, not monotonic — network-
  time-off reduces but does not remove; register for the hardening unit.
- R1-R4 (see report): no unattended retry slot for transient admission
  failures (POLICY, deliberate — zero-retry ruling stands); stale-lock
  on kill; assorted containment boundaries.

## Lens 2 — calibration/ledger (AUDIT-LEDGER.md)

- L5 HIGH: bracket selection can BORROW another window's receipts
  (global candidate scan; no runs_root/intended-pair binding) — exactly
  the defect class U1's session capability + exact binding closes.
  U1 review MUST include this scenario as a regression vector.
- L4 HIGH: pre-flight screens only a COPIED SCALAR (0.033558…), not
  the issued artifact/identity epoch/range triggers — science can run
  all night then be rejected at the morning verdict (identity epoch
  change; sub-corpus-minimum lag). Closure = memo §5A step 6 pre-science
  acceptance + D-102 trigger probe (U2) + de-duplicating the hardcoded
  literal. U2 review must include both scenarios.
- Loader itself verified correct at HEAD (issued role, file sha
  316113960c…, estimator hashes match).

## Disposition

U1/U3 in flight cover L5 and part of the mint surface. U2 covers L4's
trigger probe. R6 (absolute-paths) + R5 (monotonic time) + lock
staleness need either a small hardening unit (U1.5) or explicit
operator-procedure mitigations — decide when lens 3 lands.

## Lens 3 — extraction/mint (AUDIT-MINT.md; landed after first commit)

- Allowance arithmetic CLEAN (Decimal A_s once; component+allowance;
  max-not-sum; armwise max at claims) — no defect in inspected path.
- Confirms U3 scope: multi-cell/multi-plan minting, prefill metric,
  pinset-to-claims handoff, membership validation all missing for the
  D-117 morning chain. Exact required pinset fields documented in the
  report (feed into U3's review as the ground-truth checklist).
- Pinset `drift_allowance_j` (energy trajectory) ≠ D-102 `A_s` (timing)
  — keep the distinction in U3's schema docs.

## Paper-vs-code fidelity (AUDIT-PAPER-FIDELITY.md)

Queue for the paper diff gate (B-tier accuracy fixes before advisor
review): B1 "trapezoidal integration" → interval-average integration as
implemented; B2 publish the exact operative bracket formula; B3 narrow
the cryptographic-custody claim to what binds; quarantine is an
OPERATOR action validated by the recorder, not automatic; disclose (or
close) drift-evidence-in-verdict-hash scope; explain the policy JSON
`0.01` vs executable `0.010818` screen.
