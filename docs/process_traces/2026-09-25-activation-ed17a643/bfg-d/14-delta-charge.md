# BFG-D delta re-audit charge: fix round 1, `df33888f` → `faf0ea01`

Scope: `git diff df33888f faf0ea01`. The fix contract is `12-fix-contract-r5.md` (FX-1..FX-11). The lens findings it answers are in `11-review/`. The seat's report is `13-fix-seat-report-r5.md`; verify it, do not trust it.

Lead evidence at `faf0ea01`: 379 tests pass across the issuer, battery_float, cadence, acc_25g83_rev5, night_gate, docs_freshness, gen_state and custody_mode_inventory modules. This run includes the issuer's live identity test, which the seat's sandbox skipped.

Lead ruling on the seat's NEEDS_RULING F2: the FX-2 end-to-end test may use the same empty disposition-registry seam that the other issuer tests use, **provided** the unpatched registry-digest path is exercised elsewhere by the registry-pin tests in `tests/test_acc_25g83_rev5.py`. Verify that condition.

Answer each of the following with executed evidence:
1. Is each FX closed exactly as dictated, and does its test fail if the fix is reverted? Mutate at least FX-1, FX-2 check 5, FX-3, FX-4, FX-5 and FX-9, each in a /tmp copy.
2. Did the fix round introduce any new defect or bypass? This is the delta re-audit rule, because fix rounds introduce defects. Look especially at:
   - FX-2's working-tree pin authentication: can a pin that differs from the ledger head, or a stale pin, be recorded?
   - FX-4's derived inventory: can a finalized row's plist be skipped?
   - FX-7's new required flags: does any documented invocation in the runbook now fail?
   - FX-9's executor change: did any other probe's timeout move?
3. Same-signature statement: does any finding class from the three lenses survive anywhere else in the code? Examples are caller-chosen inputs that bypass authentication, reads before the verdict gate, and consumers missing an identity check. Grep for siblings.
4. Pin proof: `git diff --stat c6814dd8 faf0ea01 -- joulewise/calibration_bracketing.py joulewise/adapters/powermetrics.py joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/reduce.py protocol_v3.json scripts/night_chains configs` must be empty.

Constraints: read-only in the repository (/tmp is fine); no full discovery; no launchctl, powermetrics, sudo, installer or model inference; one foreground session; no subagents.

Verdict: MERGE or FIX-FIRST, with findings tiered BLOCKER / MATERIAL / NIT.
