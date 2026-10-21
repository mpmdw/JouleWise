# Executing review: L9 silly-number items 1-4 (lane/2026-10-20-l9-silly-numbers)

You are a blind, independent, executing reviewer. You did not write this code. Claim-path code: it decides whether a
printed detection floor survives a comparison. Review `git -C /tmp/jw diff d2c8460a3..090a398bb` (fetch every branch;
the lane is `lane/2026-10-20-l9-silly-numbers`, head 090a398bb, base d2c8460a3 on `lane/2026-10-13-l9-s10`).
Report: `reports/l9-silly-review/REPORT.md`. Do not edit the lane; propose fixes as diffs in the report.

What to do, executing, not only reading:
1. Check each item against the build brief below, item by item: built as written, nothing more, nothing less.
2. Run the touched test modules (JW_B5_SYNTHETIC_ONLY=1, fresh TMPDIR). Known on the base and not to chase: 28 failures
   and 3 errors in `tests/test_run_d165_closeout_from_custody.py` from historical `/Users/edr/...` custody locators absent
   in the cloud; `tests/test_r4_acceptance_oracle.py` fails 10 subtests because it hard-codes the retired 1e-12 band
   (granted to the next round). Confirm both claims by running them on base and head.
3. Replay the new zero-point predicate on production-shaped numbers: sums of order 1e1, 1e4 and 1e6 J built the way the
   three call sites build them. Show (a) a true divergence of 1e-3 J or more is still caught at every S, (b) a float
   rounding difference is not. Find the call sites' actual S: is the brief's "largest magnitude among the summed
   joule terms" what the code computes, at all three sites?
4. Check that the deleted retired-literal refusal leaves no dangling refusal code, registry entry or test, and run
   `python3.13 -m tests.hazards.refusal_census` and `tests/hazards/test_refusal_allowlist.py`.
5. Check the mint's allowance-mismatch diagnostic: a mismatch is recorded and does not refuse; a match records nothing.
6. Separately, as its own dimension: every bar the lane adds or changes carries a derivation, and sits between 1e6 times
   float noise and 1% of the smallest printed uncertainty (1e-6 J absolute where there is no half-width). A bar with no
   derivation, or tighter than float noise, is a finding.
Classify each finding: blocker (a printed number can be wrong or lost), medium, nit; and whether it is about a number or
only representation (representation-only findings are dispositioned "flag, not refuse", not sent to a fix round).

## The build brief the lane was built from
# Sol build brief: L9 silly-number items 1-4 (cloud seat, activation 4b350f47, 2026-10-20)

You are a Codex Cloud seat (gpt-6.1-sol). Repository: /workspace/JouleWise (public mpmdw/JouleWise).
Base: `git fetch origin lane/2026-10-13-l9-s10 && git checkout -b lane/2026-10-20-l9-silly-numbers d2c8460a3`
(verify `git rev-parse HEAD` is d2c8460a3bb...; stop if the commit is missing). Push ONLY to
`lane/2026-10-20-l9-silly-numbers`. Never push to any other branch. Commit as you go.

Safety: export JW_B5_SYNTHETIC_ONLY=1 for every test run. Make sure `/opt/homebrew/bin/python3.13` exists
(symlink it to python3.13 if not; the fixtures hard-code it) and set TMPDIR to a fresh directory.
Run only the test modules listed in WRITE_SCOPE (`python3.13 -m pytest <files> -q`), not the whole suite.

## Why

The project rule on numbers: every tolerance on a measured or derived quantity carries its derivation from the
quantity's physics or its printed precision. A comparison bar sits between 1e6 times the float noise and 1% of the
smallest printed uncertainty; with no half-width, 1e-6 absolute in the column's unit. A bar tighter than float noise
loses a printed number for a rounding difference. The lead decided the items below on 2026-10-15 (they were
confirmed by a second agent); you build them, you do not re-rule them.

## Governing texts, in authority order (the earlier wins on a conflict)
1. This brief.
2. The code on the base commit.
Where this brief and the code disagree on a fact (a line number, a name), the code is the fact; follow the
brief's intent and record it under "decisions I made".

## Items

1. Common-mode zero-point band. Today a zero-point comparison uses `abs_tol=1e-12` J and a failure raises
   `common_mode_zero_point_divergence_out_of_domain`, which loses a printed floor. Sites on the base:
   `joulewise/floor_extraction.py` near 628-635, `joulewise/detection_floor.py` near 1414-1421,
   `joulewise/dominance_closeout.py` near 963-965. Install ONE shared predicate, defined in
   `joulewise/detection_floor.py` (both other modules already import from it), used at all three sites:
   `math.isclose(a, b, rel_tol=1e-9, abs_tol=max(1e-6, 64 * 2**-53 * S))`, where S is the largest magnitude
   among the summed joule terms that produced the two values (write the derivation as a comment: 1e-6 J is the
   project's absolute agreement bar in joules, far under the ~1 J attribution limit; 64 ulp of S is the float
   noise of summing those terms). Add a test with a large S (sums of order 1e4-1e6 J) that fails on the base
   and passes after. Do NOT change any other 1e-12 in these files in this round (they compare bounds and
   allowances, not the zero point); list each one you saw under "left for a later round" with file:line.
2. Allowance equality in the mint (`scripts/mint_floor_artifact_generalized.py` near 2513: `Decimal(text) ==
   Decimal(str(float))`). Compare as binary64 identity: `float(Decimal(text)) == bracket_value`. A mismatch
   becomes a recorded flag in the artifact's existing flag/notes mechanism (find how the mint records
   non-refusing observations; if none exists, record it in the artifact's diagnostics and say so), not a refusal.
3. Retired-literal refusal (`RETIRED_OPERATIVE_FLOOR_LITERAL = "7.377086"`, near line 103, and its use near
   673 or wherever it is checked). It refuses a minted floor whose six-decimal text equals a retired pin. It
   protects no number. Delete the constant, the check and any refusal code that only it raises (keep a refusal
   code in a registry only if other code raises it; check with grep). Update tests that asserted the refusal.
4. Test bars (assertions on floats that are tighter than the values' meaning):
   - `tests/b5_analysis/test_mint_kept_units.py` (about 178-226): assertEqual on 16-17-digit floats becomes
     assertAlmostEqual places=9. Counts (n, t, minimum_claim_n) and guard factors stay exact.
   - `tests/b5_analysis/test_reported_cell.py` (about 151): rel 1e-12 becomes 1e-9.
   - `tests/b5_analysis/test_claim_gate_kept_quads.py` (about 338-339): places=10 becomes 6.
   - `tests/test_run_d165_closeout_from_custody.py` (about 226-254): places=12 becomes 9.
   - `tests/test_neg8_survivors.py`: places=12 checks on joule-scale sums become abs 1e-6 J.
   Integers, hashes and identical-code-on-identical-input comparisons stay exact.

## WRITE_SCOPE (exhaustive; ask for any other file by name in your report instead of editing it)
- joulewise/detection_floor.py
- joulewise/floor_extraction.py
- joulewise/dominance_closeout.py
- scripts/mint_floor_artifact_generalized.py
- tests/test_detection_floor.py
- tests/test_floor_extraction.py
- tests/test_dominance_closeout.py
- tests/test_d165_dominance_closeout.py
- tests/test_mint_floor_artifact_generalized.py
- tests/test_mint_floor_artifact_generalized_d165.py
- tests/b5_analysis/test_mint_kept_units.py
- tests/b5_analysis/test_reported_cell.py
- tests/b5_analysis/test_claim_gate_kept_quads.py
- tests/test_run_d165_closeout_from_custody.py
- tests/test_neg8_survivors.py
- .codex-report/l9-silly-numbers.md (your report)

## Checks you run
- Every test file in WRITE_SCOPE, before (record failures already present on the base) and after.
- Any other test module that imports a function you changed (find with grep); run it, do not edit it; if it
  fails because of your change, report the file and the failure.
- One end-to-end pass on production-shaped synthetic data through the real chain where the fixtures allow it
  (the floor-extraction and mint tests that build a whole synthetic window count); say which you ran.

## Report (.codex-report/l9-silly-numbers.md, committed and pushed, and as your final message)
Branch head sha; per item: done / not done, the diff summary with file:line; test results before and after
(counts and names of failures); "decisions I made"; "left for a later round"; NEEDS_RULING only for a choice
that changes which data count or a printed number.
