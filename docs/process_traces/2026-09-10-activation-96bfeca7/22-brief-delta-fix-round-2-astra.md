SESSION_MODE: delegated
WRITE_SCOPE: []
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0

# Delta re-audit of GATE-SENSIBILITY-SWEEP-01 fix rounds 1 and 2 (gpt-6-astra, high, genre review, read-only)

Range: `git diff 8da99190..58d4696b` (the two fix-round commits `558f9368` and `58d4696b` on `feat/2026-09-10-gate-sensibility-sweep`; refs are shared in this worktree — use `git show`/`git diff` with those SHAs, do not check anything out). Round 1 answered execution refuter 18 R1 (test file only: a ±10 μs capture-endpoint refusal test; the orphan `AnchorCoverageRoundingTests` class and its `reduce`/`bundle_read` imports removed). Round 2 answered the Opus contract refuter's F2/F4/F6 (docs and one comment): `docs/contracts/measurement_methodology.md` admission paragraph now states the containment RULE before its 1 μs allowance; the cooldown completion sentence is rewritten with "unit in the last place (ULP)" defined at first use and the clipped start named; `scripts/generate_g2a_probe_inputs.py` comment arithmetic corrected (750 records = 75 s at the 100 ms request; ~86 s at 115 ms).

Fix rounds introduce defects. Check, with a reproduction for anything you flag:
1. The two rewritten contract sentences against the CODE they describe (`joulewise/environment_admission.py:175–192`, `joulewise/controller.py:2516–2560`): every clause true? any clause now claims something the code does not do (e.g., the coverage term's exact composition: `max(1e-6, Σ_over_positive_overlap_contributions (ulp(evidence_end) + ulp(clipped_start)) + ulp(coverage_s))`)? Replication bar: could a reader rebuild the predicate from the text alone? First-use test: every term of art defined at or before first use in that paragraph?
2. The comment arithmetic: `ceil(75 / 0.1) = 750`; 750 × 0.115 s = 86.25 s; MIN_RATE_FIT_BASELINE_S = 60; margin claims correct?
3. Round 1's test file: still 13 tests; no import left unused (`TracePoint`, `Window`, `reduce` internals gone); the new test's inputs are ±1e-5 s at either capture edge and the expected refusal tuple matches the production reason string exactly.
4. `tests.test_docs_freshness` and any pinset over `docs/contracts/measurement_methodology.md`: does the rewrite trip a pinned digest or line reference anywhere (grep for the file's path in tests/, configs/, scripts/)?
5. Nothing else changed in the range (list `git diff --stat 8da99190..58d4696b`).

Findings by severity with reproduction; explicit "no finding" per item. Report claude-codex-report/v1, genre review, header < 8192 bytes. Read-only.
